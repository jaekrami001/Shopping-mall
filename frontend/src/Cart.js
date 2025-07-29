import React from 'react';

const Cart = ({ cart, onRemoveFromCart }) => {
  return (
    <div className="cart">
      <h2>Cart</h2>
      {cart.length === 0 ? (
        <p>Your cart is empty.</p>
      ) : (
        <ul>
          {cart.map((product) => (
            <li key={product.id}>
              <span>{product.name}</span>
              <span>${product.price}</span>
              <button onClick={() => onRemoveFromCart(product)}>Remove</button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Cart;
