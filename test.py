import tempfile
import json
import os
from pathlib import Path
from document_retival_system import parse_json, search
import traceback 

def create_test_data():
    test_documents = [
        {
            "title": "Introduction to Machine Learning",
            "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models. It enables computers to learn and improve from experience without being explicitly programmed. Common applications include image recognition, natural language processing, and predictive analytics."
        },
        {
            "title": "Deep Learning Fundamentals", 
            "content": "Deep learning uses neural networks with multiple layers to model and understand complex patterns in data. It has revolutionized fields like computer vision, speech recognition, and language translation. Popular frameworks include TensorFlow, PyTorch, and Keras."
        },
        {
            "title": "Natural Language Processing Basics",
            "content": "Natural Language Processing (NLP) is a branch of AI that helps computers understand, interpret and manipulate human language. Key techniques include tokenization, sentiment analysis, named entity recognition, and language modeling. Modern NLP relies heavily on transformer architectures."
        },
        {
            "title": "Computer Vision Applications",
            "content": "Computer vision enables machines to interpret and understand visual information from the world. Applications include facial recognition, object detection, medical image analysis, and autonomous vehicles. Convolutional neural networks are fundamental to most computer vision tasks."
        },
        {
            "title": "Data Science Methodology",
            "content": "Data science combines statistics, programming, and domain knowledge to extract insights from data. The typical workflow includes data collection, cleaning, exploration, modeling, and visualization. Popular tools include Python, R, SQL, and various machine learning libraries."
        }
    ]
    return test_documents

def test_parse_json():
    test_data = create_test_data()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        json_files = []
        
        for i, data in enumerate(test_data):
            json_file = Path(temp_dir) / f"test_doc_{i+1}.json"
            
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            json_files.append(str(json_file))
            print(f"Created: {json_file}")
        
        print("\n" + "="*50)
        print("TESTING PARSE_JSON FUNCTION")
        print("="*50)
        
        for json_file in json_files:
            print(f"\nProcessing: {Path(json_file).name}")
            try:
                result = parse_json(json_file)
                print(f"✓ Successfully parsed")
                print(f"  Title: {result.title}")
                print(f"  Summary length: {len(result.summary)} chars")
                print(f"  Content chunks: {len(result.content)}")
            except Exception as e:
                traceback.print_exc()
                print(f"✗ Error: {e}")

def test_search():
    test_questions = [
        "What is machine learning?",
        "How do neural networks work?",
        "What are NLP techniques?", 
        "What is computer vision used for?",
        "What tools are used in data science?",
        "Tell me about deep learning frameworks",
        "How does sentiment analysis work?",
        "What are convolutional neural networks?"
    ]
    
    print("\n" + "="*50)
    print("TESTING SEARCH FUNCTION")
    print("="*50)
    
    for question in test_questions:
        print(f"\nQuery: {question}")
        try:
            results = search(question, limit=3)
            if results:
                print(f"✓ Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. {result["title"]}\n{result["chunks"]}")
            else:
                print("✗ No results found")
        except Exception as e:
            print(f"✗ Error: {e}")

def main():
    print("LanceDB Test Script")
    print("="*50)
    
    try:
        test_parse_json()
        test_search()
        
        print("\n" + "="*50)
        print("TEST COMPLETED")
        print("="*50)
        
    except Exception as e:
        print(f"Test failed with error: {e}")

if __name__ == "__main__":
    main()