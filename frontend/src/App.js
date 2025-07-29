import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SearchBar = ({ onSearch, onImageSearch }) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [imageFile, setImageFile] = useState(null);
  const [searchType, setSearchType] = useState("text");

  const handleTextSearch = (e) => {
    e.preventDefault();
    onSearch({
      query: searchQuery,
      category: selectedCategory || undefined,
    });
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImageFile(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64 = event.target.result.split(',')[1];
        onImageSearch({
          image_base64: base64,
          category: selectedCategory || undefined,
        });
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="search-container">
      <div className="search-type-selector">
        <button
          className={`search-type-btn ${searchType === "text" ? "active" : ""}`}
          onClick={() => setSearchType("text")}
        >
          Text Search
        </button>
        <button
          className={`search-type-btn ${searchType === "image" ? "active" : ""}`}
          onClick={() => setSearchType("image")}
        >
          Image Search
        </button>
      </div>

      {searchType === "text" ? (
        <form onSubmit={handleTextSearch} className="search-form">
          <div className="search-inputs">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for shoes, clothes, cosmetics..."
              className="search-input"
            />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="category-select"
            >
              <option value="">All Categories</option>
              <option value="men">Men</option>
              <option value="women">Women</option>
              <option value="cosmetics">Cosmetics</option>
            </select>
            <button type="submit" className="search-btn">
              Search
            </button>
          </div>
        </form>
      ) : (
        <div className="image-search-form">
          <div className="image-upload-area">
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="image-input"
              id="image-upload"
            />
            <label htmlFor="image-upload" className="image-upload-label">
              <div className="upload-content">
                <svg className="upload-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>Upload an image to find similar products</span>
              </div>
            </label>
            {imageFile && (
              <div className="uploaded-image-preview">
                <span>Uploaded: {imageFile.name}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const ProductCard = ({ product }) => {
  return (
    <div className="product-card">
      <div className="product-image">
        <img src={product.image_url} alt={product.name} />
      </div>
      <div className="product-info">
        <h3 className="product-name">{product.name}</h3>
        <p className="product-brand">{product.brand}</p>
        <p className="product-description">{product.description}</p>
        <div className="product-price">${product.price}</div>
        <div className="product-tags">
          {product.tags.slice(0, 3).map((tag, index) => (
            <span key={index} className="product-tag">
              {tag}
            </span>
          ))}
        </div>
        <button className="add-to-cart-btn">Add to Cart</button>
      </div>
    </div>
  );
};

const CategoryFilter = ({ categories, selectedCategory, onCategoryChange }) => {
  return (
    <div className="category-filter">
      <h3>Categories</h3>
      <div className="category-buttons">
        <button
          className={`category-btn ${!selectedCategory ? "active" : ""}`}
          onClick={() => onCategoryChange("")}
        >
          All
        </button>
        {categories.map((category) => (
          <button
            key={category}
            className={`category-btn ${selectedCategory === category ? "active" : ""}`}
            onClick={() => onCategoryChange(category)}
          >
            {category.charAt(0).toUpperCase() + category.slice(1)}
          </button>
        ))}
      </div>
    </div>
  );
};

const LoginForm = ({ onLogin, onClose }) => {
  const [username, setUsername] = useState("user");
  const [password, setPassword] = useState("password");

  const handleSubmit = (e) => {
    e.preventDefault();
    onLogin(username, password);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <button onClick={onClose} className="close-btn">&times;</button>
        <h2>Login</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            required
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            required
          />
          <button type="submit">Login</button>
        </form>
      </div>
    </div>
  );
};

const CreateProductForm = ({ onCreate }) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [category, setCategory] = useState("");
  const [subcategory, setSubcategory] = useState("");
  const [brand, setBrand] = useState("");
  const [image_url, setImageUrl] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onCreate({ name, description, price: parseFloat(price), category, subcategory, brand, image_url });
  };

  return (
    <div className="create-product-form">
      <h2>Create New Product</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Name" required />
        <input type="text" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Description" required />
        <input type="number" value={price} onChange={(e) => setPrice(e.target.value)} placeholder="Price" required />
        <input type="text" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="Category" required />
        <input type="text" value={subcategory} onChange={(e) => setSubcategory(e.target.value)} placeholder="Subcategory" required />
        <input type="text" value={brand} onChange={(e) => setBrand(e.target.value)} placeholder="Brand" required />
        <input type="text" value={image_url} onChange={(e) => setImageUrl(e.target.value)} placeholder="Image URL" required />
        <button type="submit">Create Product</button>
      </form>
    </div>
  );
};

function App() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [showLogin, setShowLogin] = useState(false);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      setLoading(true);
      
      // Initialize sample products
      await axios.post(`${API}/init-products`);
      
      // Fetch products and categories
      await Promise.all([
        fetchProducts(),
        fetchCategories()
      ]);
    } catch (error) {
      console.error("Error initializing app:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async (productData) => {
    try {
      setLoading(true);
      await axios.post(`${API}/products`, productData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      await fetchProducts(selectedCategory);
    } catch (error) {
      console.error("Error creating product:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (username, password) => {
    try {
      const response = await axios.post(`${API}/token`, new URLSearchParams({
        username,
        password,
      }));
      const { access_token } = response.data;
      localStorage.setItem("token", access_token);
      setToken(access_token);
      setShowLogin(false);
    } catch (error) {
      console.error("Error logging in:", error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
  };

  const fetchProducts = async (category = "") => {
    try {
      const response = await axios.get(`${API}/products`, {
        params: category ? { category } : {}
      });
      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error("Error fetching categories:", error);
    }
  };

  const handleSearch = async (searchRequest) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/search`, searchRequest);
      setSearchResults(response.data);
    } catch (error) {
      console.error("Error searching products:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSearch = async (imageSearchRequest) => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/search/image`, imageSearchRequest);
      setSearchResults(response.data.products || []);
    } catch (error) {
      console.error("Error searching by image:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    setSearchResults(null);
    fetchProducts(category);
  };

  const displayProducts = searchResults || products;

  return (
    <div className="App">
      <header className="app-header">
        <div className="container">
          <h1 className="app-title">AI Shopping Mall</h1>
          <p className="app-subtitle">Find products with AI-powered search</p>
          <div className="auth-buttons">
            {token ? (
              <button onClick={handleLogout} className="auth-btn">Logout</button>
            ) : (
              <button onClick={() => setShowLogin(true)} className="auth-btn">Login</button>
            )}
          </div>
        </div>
      </header>

      {showLogin && <LoginForm onLogin={handleLogin} onClose={() => setShowLogin(false)} />}

      <main className="main-content">
        {token && <CreateProductForm onCreate={handleCreateProduct} />}
        <div className="container">
          <SearchBar 
            onSearch={handleSearch}
            onImageSearch={handleImageSearch}
          />

          <div className="content-layout">
            <aside className="sidebar">
              <CategoryFilter
                categories={categories}
                selectedCategory={selectedCategory}
                onCategoryChange={handleCategoryChange}
              />
            </aside>

            <section className="products-section">
              {loading ? (
                <div className="loading">
                  <div className="loading-spinner"></div>
                  <p>Loading products...</p>
                </div>
              ) : (
                <>
                  <div className="products-header">
                    <h2>
                      {searchResults ? "Search Results" : selectedCategory ? `${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Products` : "All Products"}
                      <span className="products-count">({displayProducts.length})</span>
                    </h2>
                    {searchResults && (
                      <button 
                        className="clear-search-btn"
                        onClick={() => {
                          setSearchResults(null);
                          fetchProducts(selectedCategory);
                        }}
                      >
                        Clear Search
                      </button>
                    )}
                  </div>

                  <div className="products-grid">
                    {displayProducts.map((product) => (
                      <ProductCard key={product.id} product={product} />
                    ))}
                  </div>

                  {displayProducts.length === 0 && (
                    <div className="no-products">
                      <p>No products found. Try a different search or category.</p>
                    </div>
                  )}
                </>
              )}
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;