# test_rag_system.py
"""
Comprehensive testing suite for ROCON RAG Documentation Bot
Tests all pipeline components: crawling, ingestion, vectorstore, and chat
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Tuple
import time

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


class RAGSystemTester:
    """Comprehensive RAG system testing suite."""
    
    def __init__(self):
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0
        }
        self.test_queries = self.get_test_queries()
    
    def get_test_queries(self) -> List[Dict]:
        """Define test queries with expected behaviors."""
        return [
            {
                "query": "How do I create a new site?",
                "expected_keywords": ["create", "site", "account", "plan"],
                "category": "Website Management",
                "difficulty": "easy"
            },
            {
                "query": "What is ROCON?",
                "expected_keywords": ["rocon", "platform", "paas", "wordpress"],
                "category": "Getting Started",
                "difficulty": "easy"
            },
            {
                "query": "How do I upgrade my plan?",
                "expected_keywords": ["upgrade", "plan", "billing"],
                "category": "Account Configuration",
                "difficulty": "medium"
            },
            {
                "query": "How to manage SFTP users?",
                "expected_keywords": ["sftp", "user", "manage", "file"],
                "category": "Website Management",
                "difficulty": "medium"
            },
            {
                "query": "How do I raise a support ticket?",
                "expected_keywords": ["support", "ticket", "help"],
                "category": "Support",
                "difficulty": "easy"
            },
            {
                "query": "Can I create an organization?",
                "expected_keywords": ["organization", "create", "team"],
                "category": "Organizations",
                "difficulty": "medium"
            },
            {
                "query": "What billing information can I update?",
                "expected_keywords": ["billing", "update", "payment"],
                "category": "Account Configuration",
                "difficulty": "medium"
            },
        ]
    
    # ========== PHASE 1: ENVIRONMENT & SETUP TESTS ==========
    
    def test_environment(self) -> bool:
        """Test environment setup and dependencies."""
        print_header("Phase 1: Environment & Configuration")
        
        all_passed = True
        
        # Test 1: Check Python version
        import sys
        python_version = sys.version_info
        if python_version.major == 3 and python_version.minor >= 8:
            print_success(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print_error(f"Python version too old: {python_version.major}.{python_version.minor}")
            all_passed = False
        
        # Test 2: Check required packages
        required_packages = [
            "openai", "faiss", "numpy", "tiktoken", 
            "bs4", "tqdm", "requests", "dotenv"
        ]
        
        for package in required_packages:
            try:
                __import__(package if package != "bs4" else "bs4")
                print_success(f"Package installed: {package}")
            except ImportError:
                print_error(f"Missing package: {package}")
                all_passed = False
        
        # Test 3: Check environment variables
        from app.config import OPENAI_API_KEY
        
        if OPENAI_API_KEY and len(OPENAI_API_KEY) > 20:
            print_success("OpenAI API key configured")
        else:
            print_error("OpenAI API key missing or invalid")
            all_passed = False
        
        # Test 4: Check directory structure
        required_dirs = [
            Path("data/raw_html"),
            Path("data"),
            Path("vectorstore"),
            Path("app")
        ]
        
        for dir_path in required_dirs:
            if dir_path.exists():
                print_success(f"Directory exists: {dir_path}")
            else:
                print_warning(f"Directory missing (will be created): {dir_path}")
                self.test_results["warnings"] += 1
        
        if all_passed:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
        
        return all_passed
    
    # ========== PHASE 2: CRAWLING TESTS ==========
    
    def test_crawling(self) -> bool:
        """Test documentation crawling."""
        print_header("Phase 2: Documentation Crawling")
        
        raw_html_dir = Path("data/raw_html")
        
        # Test 1: Check if HTML files exist
        if not raw_html_dir.exists():
            print_warning("No crawled HTML files found. Run crawler first:")
            print_info("  python -m app.crawl_docs")
            self.test_results["warnings"] += 1
            return False
        
        html_files = list(raw_html_dir.glob("*.html"))
        
        if len(html_files) == 0:
            print_error("No HTML files found in data/raw_html/")
            print_info("Run: python -m app.crawl_docs")
            self.test_results["failed"] += 1
            return False
        
        print_success(f"Found {len(html_files)} HTML files")
        
        # Test 2: Check file sizes
        empty_files = [f for f in html_files if f.stat().st_size < 500]
        if empty_files:
            print_warning(f"Found {len(empty_files)} suspiciously small files")
            self.test_results["warnings"] += 1
        
        # Test 3: Sample HTML quality
        sample_file = html_files[0]
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if len(content) > 1000 and '<html' in content.lower():
            print_success(f"Sample file looks valid: {sample_file.name}")
        else:
            print_error(f"Sample file may be corrupted: {sample_file.name}")
            self.test_results["failed"] += 1
            return False
        
        self.test_results["passed"] += 1
        return True
    
    # ========== PHASE 3: INGESTION TESTS ==========
    
    def test_ingestion(self) -> bool:
        """Test document ingestion and chunking."""
        print_header("Phase 3: Document Ingestion")
        
        docs_jsonl = Path("data/docs.jsonl")
        
        # Test 1: Check if docs.jsonl exists
        if not docs_jsonl.exists():
            print_warning("docs.jsonl not found. Run ingestion:")
            print_info("  python -m app.ingest")
            self.test_results["warnings"] += 1
            return False
        
        print_success("docs.jsonl exists")
        
        # Test 2: Load and validate chunks
        try:
            chunks = []
            with open(docs_jsonl, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        chunks.append(json.loads(line))
            
            print_success(f"Loaded {len(chunks)} chunks")
            
            if len(chunks) == 0:
                print_error("No chunks found in docs.jsonl")
                self.test_results["failed"] += 1
                return False
            
            # Test 3: Validate chunk structure
            required_fields = ["content", "url", "title", "category"]
            sample_chunk = chunks[0]
            
            missing_fields = [f for f in required_fields if f not in sample_chunk]
            if missing_fields:
                print_error(f"Missing fields in chunks: {missing_fields}")
                self.test_results["failed"] += 1
                return False
            
            print_success("Chunk structure is valid")
            
            # Test 4: Check chunk quality
            avg_length = sum(len(c.get("content", "")) for c in chunks) / len(chunks)
            print_success(f"Average chunk length: {avg_length:.0f} characters")
            
            if avg_length < 100:
                print_warning("Chunks seem too short. Check chunking strategy.")
                self.test_results["warnings"] += 1
            
            # Test 5: Check categories
            categories = set(c.get("category", "Unknown") for c in chunks)
            print_success(f"Found {len(categories)} categories: {', '.join(categories)}")
            
            # Test 6: Check for duplicates
            chunk_ids = [c.get("chunk_id", "") for c in chunks if c.get("chunk_id")]
            if len(chunk_ids) != len(set(chunk_ids)):
                print_warning("Found duplicate chunk IDs")
                self.test_results["warnings"] += 1
            else:
                print_success("No duplicate chunks detected")
            
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            print_error(f"Error loading docs.jsonl: {e}")
            self.test_results["failed"] += 1
            return False
    
    # ========== PHASE 4: VECTORSTORE TESTS ==========
    
    def test_vectorstore(self) -> bool:
        """Test vector database."""
        print_header("Phase 4: Vector Store")
        
        index_path = Path("vectorstore/faiss_index.bin")
        meta_path = Path("vectorstore/metadata.pkl")
        
        # Test 1: Check if index files exist
        if not index_path.exists() or not meta_path.exists():
            print_warning("Vector store not found. Build it:")
            print_info("  python -m app.vectorstore")
            self.test_results["warnings"] += 1
            return False
        
        print_success("Vector store files exist")
        
        # Test 2: Load and validate index
        try:
            from app.vectorstore import load_index
            index, payload = load_index()
            
            num_vectors = index.ntotal
            print_success(f"Loaded FAISS index with {num_vectors} vectors")
            
            if num_vectors == 0:
                print_error("Index is empty")
                self.test_results["failed"] += 1
                return False
            
            # Test 3: Validate metadata
            metadata = payload.get("metadata", [])
            chunks = payload.get("chunks", [])
            
            if len(metadata) != num_vectors:
                print_error(f"Metadata count ({len(metadata)}) doesn't match vectors ({num_vectors})")
                self.test_results["failed"] += 1
                return False
            
            print_success(f"Metadata validated ({len(metadata)} entries)")
            
            # Test 4: Test search functionality
            from app.vectorstore import search_similar
            
            test_query = "how to create site"
            results = search_similar(test_query, k=3)
            
            if len(results) > 0:
                print_success(f"Search working: found {len(results)} results for '{test_query}'")
                print_info(f"  Top result: {results[0]['title'][:60]}...")
                print_info(f"  Score: {results[0].get('vector_score', 0):.3f}")
            else:
                print_error("Search returned no results")
                self.test_results["failed"] += 1
                return False
            
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            print_error(f"Error testing vector store: {e}")
            self.test_results["failed"] += 1
            return False
    
    # ========== PHASE 5: CHAT/RAG TESTS ==========
    
    def test_chat_system(self) -> bool:
        """Test end-to-end RAG chat functionality."""
        print_header("Phase 5: RAG Chat System")
        
        try:
            from app.chat import answer_question
            
            # Test with multiple queries
            for i, test_case in enumerate(self.test_queries[:3], 1):  # Test first 3
                query = test_case["query"]
                expected_keywords = test_case["expected_keywords"]
                
                print_info(f"\nTest {i}/3: {query}")
                
                start_time = time.time()
                result = answer_question(query, use_query_expansion=True)
                elapsed = time.time() - start_time
                
                answer = result.get("answer", "")
                sources = result.get("sources", [])
                metadata = result.get("metadata", {})
                
                # Check 1: Got an answer
                if answer and len(answer) > 50:
                    print_success(f"  Got answer ({len(answer)} chars)")
                else:
                    print_error(f"  Answer too short or missing")
                    self.test_results["failed"] += 1
                    continue
                
                # Check 2: Answer contains expected keywords
                answer_lower = answer.lower()
                found_keywords = [kw for kw in expected_keywords if kw in answer_lower]
                
                if len(found_keywords) >= 2:
                    print_success(f"  Contains relevant keywords: {', '.join(found_keywords)}")
                else:
                    print_warning(f"  Few expected keywords found: {found_keywords}")
                    self.test_results["warnings"] += 1
                
                # Check 3: Has sources
                if len(sources) > 0:
                    print_success(f"  Cited {len(sources)} sources")
                else:
                    print_warning("  No sources cited")
                    self.test_results["warnings"] += 1
                
                # Check 4: Response time
                if elapsed < 5:
                    print_success(f"  Response time: {elapsed:.2f}s")
                elif elapsed < 10:
                    print_warning(f"  Slow response: {elapsed:.2f}s")
                else:
                    print_error(f"  Very slow response: {elapsed:.2f}s")
                
                # Check 5: Confidence
                confidence = metadata.get("confidence", "unknown")
                print_info(f"  Confidence: {confidence}")
                
                time.sleep(1)  # Rate limiting
            
            self.test_results["passed"] += 1
            return True
            
        except Exception as e:
            print_error(f"Error testing chat system: {e}")
            import traceback
            traceback.print_exc()
            self.test_results["failed"] += 1
            return False
    
    # ========== PHASE 6: QUALITY TESTS ==========
    
    def test_answer_quality(self) -> bool:
        """Test answer quality metrics."""
        print_header("Phase 6: Answer Quality Assessment")
        
        try:
            from app.chat import answer_question
            
            quality_scores = []
            
            for test_case in self.test_queries:
                query = test_case["query"]
                result = answer_question(query, use_query_expansion=False)  # Faster
                
                answer = result.get("answer", "")
                metadata = result.get("metadata", {})
                
                # Calculate quality score
                score = 0
                
                # Length check
                if 100 < len(answer) < 1500:
                    score += 20
                
                # Has sources
                if len(result.get("sources", [])) > 0:
                    score += 20
                
                # Confidence
                if metadata.get("confidence") == "high":
                    score += 30
                elif metadata.get("confidence") == "medium":
                    score += 15
                
                # Keyword relevance
                answer_lower = answer.lower()
                keyword_matches = sum(1 for kw in test_case["expected_keywords"] if kw in answer_lower)
                score += min(keyword_matches * 10, 30)
                
                quality_scores.append(score)
                
                status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
                print(f"{status} '{query[:40]}...': {score}/100")
                
                time.sleep(1)
            
            avg_score = sum(quality_scores) / len(quality_scores)
            
            print(f"\n📊 Average Quality Score: {avg_score:.1f}/100")
            
            if avg_score >= 70:
                print_success("Excellent answer quality!")
                self.test_results["passed"] += 1
            elif avg_score >= 50:
                print_warning("Acceptable answer quality, but room for improvement")
                self.test_results["warnings"] += 1
            else:
                print_error("Poor answer quality - review your pipeline")
                self.test_results["failed"] += 1
            
            return avg_score >= 50
            
        except Exception as e:
            print_error(f"Error in quality assessment: {e}")
            self.test_results["failed"] += 1
            return False
    
    # ========== RUN ALL TESTS ==========
    
    def run_all_tests(self):
        """Run complete test suite."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║         ROCON RAG SYSTEM - COMPREHENSIVE TESTS          ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print(f"{Colors.END}\n")
        
        start_time = time.time()
        
        # Run all test phases
        tests = [
            ("Environment", self.test_environment),
            ("Crawling", self.test_crawling),
            ("Ingestion", self.test_ingestion),
            ("Vector Store", self.test_vectorstore),
            ("Chat System", self.test_chat_system),
            ("Answer Quality", self.test_answer_quality),
        ]
        
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print_error(f"Test '{test_name}' crashed: {e}")
                self.test_results["failed"] += 1
        
        elapsed = time.time() - start_time
        
        # Print final summary
        print_header("Test Summary")
        
        total_tests = self.test_results["passed"] + self.test_results["failed"]
        
        print(f"✅ Passed: {self.test_results['passed']}/{total_tests}")
        print(f"❌ Failed: {self.test_results['failed']}/{total_tests}")
        print(f"⚠️  Warnings: {self.test_results['warnings']}")
        print(f"⏱️  Total time: {elapsed:.1f}s")
        
        if self.test_results["failed"] == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! Your RAG system is ready!{Colors.END}\n")
        elif self.test_results["failed"] <= 2:
            print(f"\n{Colors.YELLOW}⚠️  MOSTLY WORKING - Fix the failed tests{Colors.END}\n")
        else:
            print(f"\n{Colors.RED}❌ MULTIPLE FAILURES - Review your pipeline{Colors.END}\n")
        
        return self.test_results["failed"] == 0


def main():
    """Main testing entry point."""
    tester = RAGSystemTester()
    success = tester.run_all_tests()
    
    if not success:
        print_info("\n📝 Quick Fix Guide:")
        print_info("  1. Missing HTML files? Run: python -m app.crawl_docs")
        print_info("  2. Missing docs.jsonl? Run: python -m app.ingest")
        print_info("  3. Missing vector store? Run: python -m app.vectorstore")
        print_info("  4. API errors? Check your OPENAI_API_KEY in .env")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
