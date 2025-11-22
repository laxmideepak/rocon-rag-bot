from typing import List, Dict, Optional

from openai import OpenAI

import re


from .config import OPENAI_API_KEY, CHAT_MODEL, EMBED_MODEL
from .vectorstore import search_with_context, search_similar


client = OpenAI(api_key=OPENAI_API_KEY)


# Enhanced system prompt with clearer instructions
SYSTEM_PROMPT = """You are the ROCON Docs Assistant, an expert on ROCON PaaS documentation.

Your role:
- Answer questions using ONLY the provided documentation context below
- Be precise, helpful, and conversational
- Provide step-by-step instructions when explaining processes
- If the documentation clearly describes a concept but uses different terminology than the user (e.g., "site" instead of "WordPress site"), answer based on the documentation and acknowledge the terminology
- If information is partially covered, answer what you can and clearly state what's missing
- If the documentation doesn't cover the topic at all, say: "I don't see this information in the ROCON documentation. You may want to contact support at [support URL]."

Formatting guidelines:
- Use markdown formatting for better readability
- Use bullet points for lists and steps
- Include code snippets in ``` when relevant
- Bold important terms with **text**
- Always cite sources at the end with the format:

**Sources:**

- [Document Title](URL)

- [Another Document](URL)

Important: Base your answer ONLY on the provided context. Do not use external knowledge.
"""


def expand_query(original_query: str) -> List[str]:
    """
    Generate multiple query variations to improve retrieval recall.
    Uses LLM-based query expansion for better coverage.
    """
    expansion_prompt = f"""Given this user question about ROCON documentation, generate 3 alternative phrasings or related queries that would help retrieve relevant documentation.

Original question: "{original_query}"

Requirements:
- Keep queries concise (5-10 words each)
- Focus on different aspects or terminology
- Include technical and non-technical variations
- Don't change the core intent

Return only the 3 queries, one per line, without numbering or explanation."""

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # Use faster model for query expansion
            messages=[{"role": "user", "content": expansion_prompt}],
            temperature=0.3,
            max_tokens=150
        )
        
        expanded_queries = resp.choices[0].message.content.strip().split('\n')
        expanded_queries = [q.strip() for q in expanded_queries if q.strip()]
        
        # Always include original query
        all_queries = [original_query] + expanded_queries[:3]
        return all_queries
    
    except Exception as e:
        print(f"⚠️  Query expansion failed: {e}")
        return [original_query]


def normalize_query(query: str) -> str:
    """
    Normalize common variations and domain-specific terminology.
    More robust than simple string replacement.
    """
    q_norm = query.lower().strip()
    
    # Domain-specific normalization for ROCON
    replacements = {
        r'\b(wordpress|wp)\s+(site|website|instance|installation)\b': 'site',
        r'\b(wordpress|wp)\b(?!\s+(site|website))': '',  # Remove standalone "WordPress"
        r'\bwebsite\b': 'site',
        r'\baccount\b': 'account billing',
        r'\bpayment\b': 'billing payment',
        r'\bsetup\b': 'create configure',
    }
    
    for pattern, replacement in replacements.items():
        q_norm = re.sub(pattern, replacement, q_norm)
    
    # Clean up extra whitespace
    q_norm = ' '.join(q_norm.split())
    
    return q_norm if q_norm else query


def retrieve_relevant_chunks(question: str, use_expansion: bool = True) -> List[Dict]:
    """
    Retrieve relevant documentation chunks with optional query expansion.
    """
    # Normalize the query
    normalized_q = normalize_query(question)
    
    # Generate expanded queries if enabled
    if use_expansion:
        queries = expand_query(normalized_q)
        print(f"🔍 Expanded queries: {queries}")
    else:
        queries = [normalized_q]
    
    # Retrieve chunks for each query
    all_chunks = []
    seen_chunk_ids = set()
    
    for query in queries:
        # Use search_with_context for better context continuity
        chunks = search_with_context(query, k=4, expand_context=True)
        
        # Deduplicate while preserving order
        for chunk in chunks:
            chunk_id = chunk.get("chunk_id", "") + chunk.get("url", "")
            if chunk_id not in seen_chunk_ids:
                all_chunks.append(chunk)
                seen_chunk_ids.add(chunk_id)
    
    # Sort by relevance score and take top chunks
    all_chunks.sort(
        key=lambda x: x.get("rerank_score", x.get("vector_score", 0)),
        reverse=True
    )
    
    return all_chunks[:8]  # Return top 8 most relevant chunks


def build_context(chunks: List[Dict]) -> str:
    """
    Build well-structured context from retrieved chunks.
    Includes metadata for better LLM understanding.
    """
    if not chunks:
        return "No relevant documentation found."
    
    parts = []
    for i, chunk in enumerate(chunks, 1):
        # Use content with context if available
        content = chunk.get("content_with_context", chunk.get("content", ""))
        
        # Build structured context entry
        entry = f"""[Document {i}]
Title: {chunk.get('title', 'Unknown')}
Category: {chunk.get('category', 'General')}
Section: {chunk.get('heading', 'N/A')}
URL: {chunk.get('url', '')}
Relevance Score: {chunk.get('rerank_score', chunk.get('vector_score', 0)):.3f}

Content:

{content}

{'='*60}"""
        parts.append(entry)
    
    return "\n\n".join(parts)


def format_sources(chunks: List[Dict]) -> List[Dict]:
    """
    Extract and format unique sources from retrieved chunks.
    """
    sources = []
    seen_urls = set()
    
    for chunk in chunks:
        url = chunk.get("url", "")
        if url and url not in seen_urls:
            sources.append({
                "title": chunk.get("title", "Untitled"),
                "url": url,
                "category": chunk.get("category", "General")
            })
            seen_urls.add(url)
    
    return sources[:5]  # Limit to top 5 sources


def answer_question(
    question: str,
    use_query_expansion: bool = True,
    temperature: float = 0.1
) -> Dict:
    """
    Answer a user question using RAG with ROCON documentation.
    
    Args:
        question: User's question
        use_query_expansion: Whether to expand query for better retrieval
        temperature: LLM temperature (lower = more focused)
    
    Returns:
        Dict with 'answer', 'sources', and 'metadata'
    """
    print(f"\n{'='*60}")
    print(f"Question: {question}")
    print(f"{'='*60}")
    
    # Retrieve relevant documentation chunks
    chunks = retrieve_relevant_chunks(question, use_expansion=use_query_expansion)
    
    if not chunks:
        return {
            "answer": "I couldn't find relevant information in the ROCON documentation to answer your question. Please contact ROCON support for assistance.",
            "sources": [],
            "metadata": {
                "chunks_retrieved": 0,
                "confidence": "low"
            }
        }
    
    # Build context for LLM
    context = build_context(chunks)
    
    # Calculate confidence based on top chunk scores
    top_score = chunks[0].get("rerank_score", chunks[0].get("vector_score", 0))
    confidence = "high" if top_score > 0.7 else "medium" if top_score > 0.5 else "low"
    
    print(f"📊 Retrieved {len(chunks)} chunks | Top score: {top_score:.3f} | Confidence: {confidence}")
    
    # Prepare messages for LLM
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""User Question: {question}

Documentation Context:

{context}

Instructions:
1. Answer the user's question using ONLY the documentation context above
2. Be clear, concise, and helpful
3. Use markdown formatting for better readability
4. If the documentation uses different terminology than the user's question, acknowledge this in your answer
5. Include a "Sources" section at the end with markdown links
6. If the context doesn't fully answer the question, be explicit about what's missing

Your answer:"""
        }
    ]
    
    # Get response from LLM
    try:
        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=1000
        )
        
        answer = resp.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Error generating answer: {e}")
        return {
            "answer": "I encountered an error while generating the answer. Please try again.",
            "sources": format_sources(chunks),
            "metadata": {
                "error": str(e),
                "chunks_retrieved": len(chunks),
                "confidence": confidence
            }
        }
    
    # Format sources
    sources = format_sources(chunks)
    
    # Return complete response
    return {
        "answer": answer,
        "sources": sources,
        "metadata": {
            "chunks_retrieved": len(chunks),
            "confidence": confidence,
            "top_score": float(top_score),
            "query_expanded": use_query_expansion
        }
    }


def interactive_chat():
    """
    Interactive chat loop for testing.
    """
    print("\n" + "="*60)
    print("ROCON Docs Assistant - Interactive Mode")
    print("Type 'quit' or 'exit' to stop")
    print("="*60 + "\n")
    
    while True:
        question = input("\n💬 Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not question:
            continue
        
        # Get answer
        result = answer_question(question)
        
        # Display answer
        print("\n" + "="*60)
        print("📝 Answer:")
        print("="*60)
        print(result["answer"])
        
        # Display metadata
        print(f"\n📊 Metadata:")
        print(f"   Confidence: {result['metadata']['confidence']}")
        print(f"   Chunks used: {result['metadata']['chunks_retrieved']}")
        print(f"   Top score: {result['metadata']['top_score']:.3f}")


if __name__ == "__main__":
    # Run interactive chat
    interactive_chat()
