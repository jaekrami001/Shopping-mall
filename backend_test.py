#!/usr/bin/env python3
"""
Backend API Testing for AI Shopping Mall
Tests all backend endpoints for functionality and data integrity
"""

import requests
import json
import base64
from typing import Dict, List, Any
import sys

# Backend URL from environment
BACKEND_URL = "https://4fd3ceef-9912-4f8b-a9b6-bc2d0a085278.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str, details: Dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_health_check(self):
        """Test basic API health check"""
        try:
            response = self.session.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Health Check", True, "API is responding correctly", 
                                {"status_code": response.status_code, "response": data})
                    return True
                else:
                    self.log_test("Health Check", False, "Invalid response format", 
                                {"status_code": response.status_code, "response": data})
                    return False
            else:
                self.log_test("Health Check", False, f"HTTP {response.status_code}", 
                            {"status_code": response.status_code, "response": response.text})
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False

    def test_init_products(self):
        """Test sample product initialization"""
        try:
            response = self.session.post(f"{BACKEND_URL}/init-products")
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "8 sample products" in data["message"]:
                    self.log_test("Sample Product Initialization", True, 
                                "8 sample products initialized successfully", 
                                {"response": data})
                    return True
                else:
                    self.log_test("Sample Product Initialization", False, 
                                "Unexpected response format or count", 
                                {"response": data})
                    return False
            else:
                self.log_test("Sample Product Initialization", False, 
                            f"HTTP {response.status_code}", 
                            {"status_code": response.status_code, "response": response.text})
                return False
        except Exception as e:
            self.log_test("Sample Product Initialization", False, f"Error: {str(e)}")
            return False

    def test_get_all_products(self):
        """Test fetching all products"""
        try:
            response = self.session.get(f"{BACKEND_URL}/products")
            if response.status_code == 200:
                products = response.json()
                if isinstance(products, list) and len(products) == 8:
                    # Verify product structure
                    required_fields = ["id", "name", "description", "price", "category", "brand"]
                    sample_product = products[0]
                    missing_fields = [field for field in required_fields if field not in sample_product]
                    
                    if not missing_fields:
                        self.log_test("Get All Products", True, 
                                    f"Retrieved {len(products)} products with correct structure", 
                                    {"product_count": len(products), "sample_product": sample_product})
                        return products
                    else:
                        self.log_test("Get All Products", False, 
                                    f"Missing required fields: {missing_fields}", 
                                    {"missing_fields": missing_fields, "sample_product": sample_product})
                        return None
                else:
                    self.log_test("Get All Products", False, 
                                f"Expected 8 products, got {len(products) if isinstance(products, list) else 'non-list'}", 
                                {"response": products})
                    return None
            else:
                self.log_test("Get All Products", False, f"HTTP {response.status_code}", 
                            {"status_code": response.status_code, "response": response.text})
                return None
        except Exception as e:
            self.log_test("Get All Products", False, f"Error: {str(e)}")
            return None

    def test_category_filtering(self):
        """Test product filtering by category"""
        categories_to_test = ["men", "women", "cosmetics"]
        
        for category in categories_to_test:
            try:
                response = self.session.get(f"{BACKEND_URL}/products?category={category}")
                if response.status_code == 200:
                    products = response.json()
                    if isinstance(products, list) and len(products) > 0:
                        # Verify all products belong to the requested category
                        wrong_category = [p for p in products if p.get("category") != category]
                        if not wrong_category:
                            self.log_test(f"Category Filter - {category}", True, 
                                        f"Retrieved {len(products)} products for category '{category}'", 
                                        {"product_count": len(products), "category": category})
                        else:
                            self.log_test(f"Category Filter - {category}", False, 
                                        f"Found {len(wrong_category)} products with wrong category", 
                                        {"wrong_products": wrong_category})
                    else:
                        self.log_test(f"Category Filter - {category}", False, 
                                    f"No products found for category '{category}'", 
                                    {"response": products})
                else:
                    self.log_test(f"Category Filter - {category}", False, 
                                f"HTTP {response.status_code}", 
                                {"status_code": response.status_code})
            except Exception as e:
                self.log_test(f"Category Filter - {category}", False, f"Error: {str(e)}")

    def test_text_search(self):
        """Test text-based product search"""
        search_queries = [
            {"query": "shoes", "expected_min": 2, "description": "shoes search"},
            {"query": "dress", "expected_min": 1, "description": "dress search"},
            {"query": "cosmetics", "expected_min": 1, "description": "cosmetics search"},
            {"query": "leather", "expected_min": 1, "description": "leather search"},
            {"query": "premium", "expected_min": 2, "description": "premium search"}
        ]
        
        for search_data in search_queries:
            try:
                payload = {"query": search_data["query"]}
                response = self.session.post(f"{BACKEND_URL}/search", json=payload)
                
                if response.status_code == 200:
                    products = response.json()
                    if isinstance(products, list) and len(products) >= search_data["expected_min"]:
                        self.log_test(f"Text Search - {search_data['description']}", True, 
                                    f"Found {len(products)} products for query '{search_data['query']}'", 
                                    {"query": search_data["query"], "result_count": len(products)})
                    else:
                        self.log_test(f"Text Search - {search_data['description']}", False, 
                                    f"Expected at least {search_data['expected_min']} products, got {len(products) if isinstance(products, list) else 'non-list'}", 
                                    {"query": search_data["query"], "response": products})
                else:
                    self.log_test(f"Text Search - {search_data['description']}", False, 
                                f"HTTP {response.status_code}", 
                                {"status_code": response.status_code, "query": search_data["query"]})
            except Exception as e:
                self.log_test(f"Text Search - {search_data['description']}", False, f"Error: {str(e)}")

    def test_search_with_filters(self):
        """Test search with category and price filters"""
        test_cases = [
            {
                "query": "shoes",
                "category": "men",
                "description": "men's shoes search"
            },
            {
                "query": "premium",
                "max_price": 100.0,
                "description": "premium items under $100"
            },
            {
                "query": "luxury",
                "min_price": 200.0,
                "description": "luxury items over $200"
            }
        ]
        
        for test_case in test_cases:
            try:
                payload = {k: v for k, v in test_case.items() if k not in ["description"]}
                response = self.session.post(f"{BACKEND_URL}/search", json=payload)
                
                if response.status_code == 200:
                    products = response.json()
                    if isinstance(products, list):
                        # Verify filters are applied correctly
                        filter_errors = []
                        
                        for product in products:
                            if "category" in payload and product.get("category") != payload["category"]:
                                filter_errors.append(f"Wrong category: {product.get('category')}")
                            if "max_price" in payload and product.get("price", 0) > payload["max_price"]:
                                filter_errors.append(f"Price too high: {product.get('price')}")
                            if "min_price" in payload and product.get("price", 0) < payload["min_price"]:
                                filter_errors.append(f"Price too low: {product.get('price')}")
                        
                        if not filter_errors:
                            self.log_test(f"Search with Filters - {test_case['description']}", True, 
                                        f"Found {len(products)} products with correct filters applied", 
                                        {"filters": payload, "result_count": len(products)})
                        else:
                            self.log_test(f"Search with Filters - {test_case['description']}", False, 
                                        f"Filter validation failed: {filter_errors[:3]}", 
                                        {"filters": payload, "errors": filter_errors[:3]})
                    else:
                        self.log_test(f"Search with Filters - {test_case['description']}", False, 
                                    "Invalid response format", 
                                    {"filters": payload, "response": products})
                else:
                    self.log_test(f"Search with Filters - {test_case['description']}", False, 
                                f"HTTP {response.status_code}", 
                                {"status_code": response.status_code, "filters": payload})
            except Exception as e:
                self.log_test(f"Search with Filters - {test_case['description']}", False, f"Error: {str(e)}")

    def test_categories_endpoint(self):
        """Test categories listing endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/categories")
            if response.status_code == 200:
                data = response.json()
                if "categories" in data and "subcategories" in data:
                    categories = data["categories"]
                    subcategories = data["subcategories"]
                    
                    expected_categories = ["men", "women", "cosmetics"]
                    missing_categories = [cat for cat in expected_categories if cat not in categories]
                    
                    if not missing_categories and len(categories) >= 3:
                        self.log_test("Categories Endpoint", True, 
                                    f"Retrieved {len(categories)} categories and {len(subcategories)} subcategories", 
                                    {"categories": categories, "subcategories": subcategories})
                        return True
                    else:
                        self.log_test("Categories Endpoint", False, 
                                    f"Missing expected categories: {missing_categories}", 
                                    {"categories": categories, "missing": missing_categories})
                        return False
                else:
                    self.log_test("Categories Endpoint", False, 
                                "Invalid response format - missing categories or subcategories", 
                                {"response": data})
                    return False
            else:
                self.log_test("Categories Endpoint", False, f"HTTP {response.status_code}", 
                            {"status_code": response.status_code, "response": response.text})
                return False
        except Exception as e:
            self.log_test("Categories Endpoint", False, f"Error: {str(e)}")
            return False

    def test_image_search_placeholder(self):
        """Test image search placeholder endpoint"""
        try:
            # Create a dummy base64 image string
            dummy_image = base64.b64encode(b"dummy_image_data").decode('utf-8')
            payload = {
                "image_base64": dummy_image,
                "category": "women"
            }
            
            response = self.session.post(f"{BACKEND_URL}/search/image", json=payload)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "products" in data:
                    products = data["products"]
                    if isinstance(products, list):
                        self.log_test("Image Search Placeholder", True, 
                                    f"Placeholder endpoint working - returned {len(products)} products", 
                                    {"message": data["message"], "product_count": len(products)})
                        return True
                    else:
                        self.log_test("Image Search Placeholder", False, 
                                    "Products field is not a list", 
                                    {"response": data})
                        return False
                else:
                    self.log_test("Image Search Placeholder", False, 
                                "Missing message or products in response", 
                                {"response": data})
                    return False
            else:
                self.log_test("Image Search Placeholder", False, f"HTTP {response.status_code}", 
                            {"status_code": response.status_code, "response": response.text})
                return False
        except Exception as e:
            self.log_test("Image Search Placeholder", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all backend tests in sequence"""
        print("🚀 Starting AI Shopping Mall Backend Tests")
        print("=" * 60)
        
        # Test 1: Health check
        if not self.test_health_check():
            print("❌ Backend is not responding. Stopping tests.")
            return False
        
        # Test 2: Initialize products
        self.test_init_products()
        
        # Test 3: Get all products
        products = self.test_get_all_products()
        
        # Test 4: Category filtering
        self.test_category_filtering()
        
        # Test 5: Text search
        self.test_text_search()
        
        # Test 6: Search with filters
        self.test_search_with_filters()
        
        # Test 7: Categories endpoint
        self.test_categories_endpoint()
        
        # Test 8: Image search placeholder
        self.test_image_search_placeholder()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")
        
        return passed == total

if __name__ == "__main__":
    tester = BackendTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)