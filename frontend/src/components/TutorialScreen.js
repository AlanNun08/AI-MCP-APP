import React, { useState } from 'react';

const TutorialScreen = ({ setCurrentScreen, showNotification }) => {
  const [activeSection, setActiveSection] = useState('recipes');

  const sections = {
    recipes: {
      title: '🍳 Recipe Generator',
      icon: '🍳',
      content: (
        <div>
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🍳</div>
            <h3 className="text-3xl font-bold text-gray-800">AI Recipe Generator</h3>
            <p className="text-lg text-gray-600">Create personalized recipes with automatic shopping lists</p>
          </div>
          
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-orange-50 rounded-xl p-4 text-center">
                <div className="text-3xl mb-2">🍝</div>
                <h4 className="font-bold text-gray-800">Cuisine</h4>
                <p className="text-sm text-gray-600">Traditional dishes from around the world</p>
              </div>
              <div className="bg-purple-50 rounded-xl p-4 text-center">
                <div className="text-3xl mb-2">🍪</div>
                <h4 className="font-bold text-gray-800">Snacks</h4>
                <p className="text-sm text-gray-600">Healthy bowls, treats, and bites</p>
              </div>
              <div className="bg-blue-50 rounded-xl p-4 text-center">
                <div className="text-3xl mb-2">🧋</div>
                <h4 className="font-bold text-gray-800">Beverages</h4>
                <p className="text-sm text-gray-600">Boba, tea, and specialty drinks</p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
              <h4 className="font-bold text-gray-800 mb-4">📋 Step-by-Step Guide:</h4>
              <div className="space-y-3">
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">1</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Choose Recipe Category</h5>
                    <p className="text-gray-600 text-sm">Select from Cuisine, Snacks, or Beverages</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">2</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Customize Your Recipe</h5>
                    <p className="text-gray-600 text-sm">Add dietary preferences, difficulty level, and ingredients you have</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">3</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Generate Recipe</h5>
                    <p className="text-gray-600 text-sm">AI creates a personalized recipe with ingredients and instructions</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">4</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Shop with Walmart</h5>
                    <p className="text-gray-600 text-sm">Automatically generated shopping cart with all ingredients</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    starbucks: {
      title: '☕ Starbucks Secret Menu',
      icon: '☕',
      content: (
        <div>
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">☕</div>
            <h3 className="text-3xl font-bold text-green-800">Starbucks Secret Menu Generator</h3>
            <p className="text-lg text-gray-600">Create viral TikTok-worthy drink hacks with drive-thru scripts</p>
          </div>
          
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">🥤</div>
                <p className="text-sm font-medium">Frappuccino</p>
              </div>
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">🧊</div>
                <p className="text-sm font-medium">Refresher</p>
              </div>
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">🍋</div>
                <p className="text-sm font-medium">Lemonade</p>
              </div>
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">🍵</div>
                <p className="text-sm font-medium">Matcha Latte</p>
              </div>
              <div className="bg-green-50 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">🎲</div>
                <p className="text-sm font-medium">Surprise Me!</p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6">
              <h4 className="font-bold text-gray-800 mb-4">🎯 How to Use:</h4>
              <div className="space-y-3">
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">1</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Choose Drink Type</h5>
                    <p className="text-gray-600 text-sm">Select from Frappuccino, Refresher, Lemonade, Matcha Latte, or Surprise Me!</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">2</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Add Flavor Inspiration (Optional)</h5>
                    <p className="text-gray-600 text-sm">Try "birthday cake", "tres leches", "ube", or "cookies and cream"</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">3</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Generate Your Drink</h5>
                    <p className="text-gray-600 text-sm">AI creates a unique drink with ordering script and modifications</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">4</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Copy & Order</h5>
                    <p className="text-gray-600 text-sm">Copy the exact script and use it at any Starbucks drive-thru!</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-purple-50 rounded-xl p-6">
              <h4 className="font-bold text-gray-800 mb-3">🌟 What You Get:</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <p className="text-gray-700">• 🎨 Creative drink name</p>
                  <p className="text-gray-700">• 📝 Exact ordering script</p>
                  <p className="text-gray-700">• 🛠️ Step-by-step modifications</p>
                </div>
                <div className="space-y-2">
                  <p className="text-gray-700">• 💡 Pro ordering tips</p>
                  <p className="text-gray-700">• 🔥 Why it's amazing</p>
                  <p className="text-gray-700">• 📱 Easy sharing for TikTok</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    walmart: {
      title: '🛒 Walmart Integration',
      icon: '🛒',
      content: (
        <div>
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🛒</div>
            <h3 className="text-3xl font-bold text-blue-800">Walmart Shopping Integration</h3>
            <p className="text-lg text-gray-600">Automatic shopping lists for all your recipes</p>
          </div>
          
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-6">
              <h4 className="font-bold text-gray-800 mb-4">🔄 How It Works:</h4>
              <div className="space-y-3">
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">1</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Generate Recipe</h5>
                    <p className="text-gray-600 text-sm">Create any recipe using the AI Recipe Generator</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">2</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">AI Finds Ingredients</h5>
                    <p className="text-gray-600 text-sm">Automatically searches Walmart for all recipe ingredients</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">3</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">Choose Your Products</h5>
                    <p className="text-gray-600 text-sm">Select from multiple options for each ingredient</p>
                  </div>
                </div>
                <div className="flex items-start">
                  <span className="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-0.5">4</span>
                  <div>
                    <h5 className="font-semibold text-gray-800">One-Click Shopping</h5>
                    <p className="text-gray-600 text-sm">Click the Walmart link to add all items to your cart</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-red-50 border-l-4 border-red-400 rounded-lg p-6">
              <div className="flex items-start">
                <div className="text-3xl mr-4">⚠️</div>
                <div>
                  <h4 className="font-bold text-red-800 mb-3">CRITICAL: Walmart Login Required</h4>
                  <p className="text-red-700 mb-4">
                    For the shopping cart to work properly, you MUST be logged into your Walmart account:
                  </p>
                  
                  <div className="bg-white rounded-lg p-4 space-y-3">
                    <div className="flex items-start">
                      <span className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">1</span>
                      <div>
                        <h5 className="font-semibold text-red-800">Open New Tab</h5>
                        <p className="text-red-700 text-sm">Go to <strong>walmart.com</strong> in a separate browser tab</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <span className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">2</span>
                      <div>
                        <h5 className="font-semibold text-red-800">Log Into Walmart</h5>
                        <p className="text-red-700 text-sm">Sign in with your Walmart account credentials</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <span className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">3</span>
                      <div>
                        <h5 className="font-semibold text-red-800">Return to AI Chef</h5>
                        <p className="text-red-700 text-sm">Come back to this tab and click the Walmart shopping link</p>
                      </div>
                    </div>
                    <div className="flex items-start">
                      <span className="w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">4</span>
                      <div>
                        <h5 className="font-semibold text-red-800">Items Added to Cart</h5>
                        <p className="text-red-700 text-sm">All selected ingredients will appear in your Walmart cart</p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 p-3 bg-red-100 rounded-lg">
                    <p className="text-red-800 font-semibold">
                      🚨 Without logging in first, the cart link won't work and items won't be added!
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-green-50 rounded-xl p-6">
              <h4 className="font-bold text-gray-800 mb-3">✅ Pro Tips:</h4>
              <div className="space-y-2">
                <p className="text-gray-700">• 🔄 Keep your Walmart tab open while browsing AI Chef</p>
                <p className="text-gray-700">• 🛒 Review your cart before checkout</p>
                <p className="text-gray-700">• 📦 Choose pickup or delivery options at Walmart</p>
                <p className="text-gray-700">• 💰 Check for deals and coupons on Walmart.com</p>
              </div>
            </div>
          </div>
        </div>
      )
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-4">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <button
            onClick={() => setCurrentScreen('dashboard')}
            className="mb-4 inline-flex items-center text-gray-600 hover:text-gray-800 font-medium"
          >
            <span className="mr-2">←</span>
            Back to Dashboard
          </button>
          <div className="text-6xl mb-4">📚</div>
          <h1 className="text-4xl font-bold text-gray-800 mb-2">How to Use AI Chef</h1>
          <p className="text-lg text-gray-600">Master all features with this comprehensive guide</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-6">
              <h3 className="font-bold text-gray-800 mb-4">Tutorial Sections</h3>
              <div className="space-y-2">
                {Object.entries(sections).map(([key, section]) => (
                  <button
                    key={key}
                    onClick={() => setActiveSection(key)}
                    className={`w-full text-left p-3 rounded-xl transition-all duration-200 ${
                      activeSection === key
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                        : 'bg-gray-50 hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center">
                      <span className="text-xl mr-3">{section.icon}</span>
                      <span className="font-medium">{section.title}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-2xl shadow-lg p-8">
              {sections[activeSection].content}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-2xl shadow-lg p-6">
          <h3 className="text-2xl font-bold text-gray-800 mb-4 text-center">Ready to Start?</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              onClick={() => setCurrentScreen('recipe-generation')}
              className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold py-4 px-6 rounded-xl transition-all duration-200"
            >
              🍳 Generate Recipe
            </button>
            <button
              onClick={() => setCurrentScreen('starbucks-generator')}
              className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-bold py-4 px-6 rounded-xl transition-all duration-200"
            >
              ☕ Create Starbucks Drink
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TutorialScreen;