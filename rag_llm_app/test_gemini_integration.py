#!/usr/bin/env python3
"""Quick test to verify Gemini integration is working"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.embeddings.factory import get_embedder
from app.llm.factory import get_generator


def test_embedder():
    """Test Gemini embedder"""
    print("\n🧪 Testing Gemini Embedder...")
    
    try:
        embedder = get_embedder()
        
        # Test single embedding
        test_text = "Machine learning is a subset of artificial intelligence"
        embedding = embedder.embed_text(test_text)
        
        print(f"✅ Single text embedding successful")
        print(f"   - Text: {test_text}")
        print(f"   - Embedding dimension: {embedding.shape[0]}")
        print(f"   - Expected dimension: {settings.GEMINI_EMBEDDING_DIMENSION}")
        
        # Test batch embeddings
        test_chunks = [
            "Python is a popular programming language",
            "Machine learning requires large datasets",
            "Neural networks are inspired by the brain"
        ]
        
        embeddings = embedder.embed_chunks(test_chunks)
        print(f"\n✅ Batch embedding successful")
        print(f"   - Number of chunks: {len(test_chunks)}")
        print(f"   - Number of embeddings: {len(embeddings)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embedder test failed: {e}")
        return False


def test_generator():
    """Test Gemini generator"""
    print("\n🧪 Testing Gemini Generator...")
    
    try:
        generator = get_generator()
        
        # Test simple generation
        prompt = "What is artificial intelligence? Answer in one sentence."
        response = generator.generate(prompt)
        
        print(f"✅ Text generation successful")
        print(f"   - Prompt: {prompt}")
        print(f"   - Response: {response[:100]}...")
        
        # Test question answering
        context = "Python is a high-level programming language known for its simplicity and readability."
        question = "What is Python?"
        answer = generator.answer_question(question, context=context)
        
        print(f"\n✅ Question answering successful")
        print(f"   - Context: {context}")
        print(f"   - Question: {question}")
        print(f"   - Answer: {answer[:100]}...")
        
        # Test summarization
        long_text = """
        The human brain is one of the most complex organs in the body. It controls thoughts, 
        memories, emotions, touch, motor skills, vision, respiration, and every process that 
        regulates our body. The brain is made up of approximately 86 billion neurons and 
        trillions of glial cells that provide support and insulation for the neurons.
        """
        summary = generator.summarize(long_text)
        
        print(f"\n✅ Summarization successful")
        print(f"   - Original length: {len(long_text)} characters")
        print(f"   - Summary: {summary[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Generator test failed: {e}")
        return False


def test_config():
    """Test that Gemini is properly configured"""
    print("\n🧪 Testing Gemini Configuration...")
    
    try:
        # Check settings
        print(f"✅ Configuration loaded")
        print(f"   - MODEL_BACKEND: {settings.MODEL_BACKEND}")
        print(f"   - GEMINI_API_KEY: {'*' * 10 if settings.GEMINI_API_KEY else 'NOT SET'}")
        print(f"   - GEMINI_EMBEDDING_MODEL: {settings.GEMINI_EMBEDDING_MODEL}")
        print(f"   - GEMINI_EMBEDDING_DIMENSION: {settings.GEMINI_EMBEDDING_DIMENSION}")
        print(f"   - GEMINI_LLM_MODEL: {settings.GEMINI_LLM_MODEL}")
        
        # Validate settings
        settings.validate()
        print(f"✅ Settings validation passed")
        
        # Check if using gemini backend
        if settings.MODEL_BACKEND != "gemini":
            print(f"\n⚠️  WARNING: MODEL_BACKEND is '{settings.MODEL_BACKEND}', not 'gemini'")
            print(f"   - Set MODEL_BACKEND=gemini in .env to use Gemini API")
            return False
        
        # Check if API key is set
        if not settings.GEMINI_API_KEY:
            print(f"\n❌ ERROR: GEMINI_API_KEY is not set")
            print(f"   - Add GEMINI_API_KEY=your_key to .env")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Gemini Integration Test")
    print("=" * 60)
    
    # Test configuration
    config_ok = test_config()
    
    if not config_ok:
        print("\n" + "=" * 60)
        print("⚠️  Configuration test failed")
        print("Please check your .env file and set up Gemini API key")
        print("See GEMINI_SETUP_GUIDE.md for detailed instructions")
        print("=" * 60)
        return 1
    
    # Test embedder
    embedder_ok = test_embedder()
    
    # Test generator
    generator_ok = test_generator()
    
    # Summary
    print("\n" + "=" * 60)
    
    if embedder_ok and generator_ok:
        print("✅ All tests passed!")
        print("Gemini integration is working correctly")
    else:
        print("❌ Some tests failed")
        print("Check error messages above for details")
    
    print("=" * 60)
    
    return 0 if (embedder_ok and generator_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
