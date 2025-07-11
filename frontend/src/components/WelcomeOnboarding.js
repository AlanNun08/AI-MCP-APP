import React, { useState } from 'react';

const WelcomeOnboarding = ({ user, setCurrentScreen, showNotification }) => {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: "Welcome to AI Chef! 🍳",
      content: (
        <div className="text-center">
          <div className="text-8xl mb-6">🎉</div>
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Welcome, {user?.first_name}!
          </h2>
          <p className="text-xl text-gray-600 mb-6">
            You've just joined the most exciting cooking adventure! 
          </p>
          <div className="bg-gradient-to-r from-orange-100 to-red-100 rounded-2xl p-6 mb-6">
            <p className="text-lg text-gray-700 leading-relaxed">
              AI Chef is your personal cooking assistant that generates <span className="font-bold text-orange-600">custom recipes</span>, 
              creates <span className="font-bold text-green-600">Starbucks secret menu drinks</span>, 
              and automatically builds <span className="font-bold text-blue-600">Walmart shopping carts</span> for you!
            </p>
          </div>
          <p className="text-gray-600">Let's take a quick tour to get you started! 🚀</p>
        </div>
      )
    },
    {
      title: "🍝 AI Recipe Generator",
      content: (
        <div>
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🍳</div>
            <h3 className="text-3xl font-bold text-gray-800 mb-4">Generate Amazing Recipes</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="text-center p-4 bg-orange-50 rounded-xl">
              <div className="text-3xl mb-2">🍝</div>
              <h4 className="font-bold text-gray-800">Cuisine</h4>
              <p className="text-sm text-gray-600">Traditional dishes from around the world</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-xl">
              <div className="text-3xl mb-2">🍪</div>
              <h4 className="font-bold text-gray-800">Snacks</h4>
              <p className="text-sm text-gray-600">Healthy bowls, treats, and bites</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-xl">
              <div className="text-3xl mb-2">🧋</div>
              <h4 className="font-bold text-gray-800">Beverages</h4>
              <p className="text-sm text-gray-600">Boba, tea, and specialty drinks</p>
            </div>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6">
            <h4 className="font-bold text-gray-800 mb-3">✨ How it works:</h4>
            <div className="space-y-2 text-gray-700">
              <p>• 🎯 Choose your recipe category (Cuisine, Snacks, or Beverages)</p>
              <p>• 🎨 Customize with dietary preferences, ingredients, and difficulty</p>
              <p>• 🤖 AI generates a personalized recipe just for you</p>
              <p>• 🛒 Automatically creates a Walmart shopping cart with all ingredients</p>
              <p>• 🏪 One-click shopping - all ingredients ready to purchase!</p>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "☕ Starbucks Secret Menu",
      content: (
        <div>
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">☕</div>
            <h3 className="text-3xl font-bold text-green-800 mb-4">Viral TikTok Drink Hacks</h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl mb-1">🥤</div>
              <p className="text-sm font-medium">Frappuccino</p>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl mb-1">🧊</div>
              <p className="text-sm font-medium">Refresher</p>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl mb-1">🍋</div>
              <p className="text-sm font-medium">Lemonade</p>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl mb-1">🍵</div>
              <p className="text-sm font-medium">Matcha Latte</p>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl mb-1">🎲</div>
              <p className="text-sm font-medium">Surprise Me!</p>
            </div>
          </div>

          <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-xl p-6 mb-6">
            <h4 className="font-bold text-gray-800 mb-3">🎯 What you get:</h4>
            <div className="space-y-2 text-gray-700">
              <p>• 🌟 Creative drink name (like "Unicorn Dreams Frappuccino")</p>
              <p>• 📝 Exact drive-thru ordering script</p>
              <p>• 🎨 Step-by-step modifications to request</p>
              <p>• 💡 Pro tips for the best results</p>
              <p>• 📱 Easy copy & share for TikTok</p>
            </div>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
            <div className="flex items-start">
              <div className="text-2xl mr-3">🎬</div>
              <div>
                <h4 className="font-bold text-gray-800">Drive-Thru Ready!</h4>
                <p className="text-gray-700">Each drink comes with a perfect ordering script you can use at any Starbucks drive-thru. Just copy and paste!</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "🛒 Walmart Shopping Integration",
      content: (
        <div>
          <div className="text-center mb-6">
            <div className="text-6xl mb-4">🛒</div>
            <h3 className="text-3xl font-bold text-blue-800 mb-4">Automatic Shopping Lists</h3>
          </div>

          <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-xl p-6 mb-6">
            <h4 className="font-bold text-gray-800 mb-3">🔄 How it works:</h4>
            <div className="space-y-3 text-gray-700">
              <div className="flex items-start">
                <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">1</span>
                <p>Generate a recipe with AI Chef</p>
              </div>
              <div className="flex items-start">
                <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">2</span>
                <p>AI automatically finds all ingredients at Walmart</p>
              </div>
              <div className="flex items-start">
                <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">3</span>
                <p>Choose your preferred products from multiple options</p>
              </div>
              <div className="flex items-start">
                <span className="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-3 mt-0.5">4</span>
                <p>One-click to add everything to your Walmart cart</p>
              </div>
            </div>
          </div>

          <div className="bg-red-50 border-l-4 border-red-400 p-6 rounded-lg">
            <div className="flex items-start">
              <div className="text-2xl mr-3">⚠️</div>
              <div>
                <h4 className="font-bold text-red-800 mb-2">IMPORTANT: Walmart Login Required</h4>
                <p className="text-red-700 mb-3">
                  To add items to your Walmart cart, you must be logged into your Walmart account:
                </p>
                <div className="bg-white rounded-lg p-4 space-y-2">
                  <p className="text-red-700">• 🔗 <strong>Open a new tab</strong> and go to <strong>walmart.com</strong></p>
                  <p className="text-red-700">• 🔐 <strong>Log into your Walmart account</strong></p>
                  <p className="text-red-700">• 🔙 <strong>Come back to AI Chef</strong> and click the Walmart link</p>
                  <p className="text-red-700">• 🛒 <strong>Items will be added to your logged-in cart</strong></p>
                </div>
                <p className="text-red-600 mt-3 font-medium">
                  Without logging in, the cart link won't work properly!
                </p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      title: "🎯 Ready to Start!",
      content: (
        <div className="text-center">
          <div className="text-8xl mb-6">🚀</div>
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            You're All Set, {user?.first_name}!
          </h2>
          <p className="text-xl text-gray-600 mb-6">
            Time to create some amazing recipes and viral Starbucks drinks!
          </p>
          
          <div className="bg-gradient-to-r from-green-100 to-blue-100 rounded-2xl p-6 mb-6">
            <h3 className="text-2xl font-bold text-gray-800 mb-4">Quick Start Guide:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left">
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-bold text-green-600 mb-2">🍳 For Recipes:</h4>
                <p className="text-gray-700 text-sm">Click "Generate Recipe" → Choose category → Customize options → Get shopping list!</p>
              </div>
              <div className="bg-white rounded-lg p-4">
                <h4 className="font-bold text-green-600 mb-2">☕ For Starbucks:</h4>
                <p className="text-gray-700 text-sm">Click "Starbucks Secret Menu" → Pick drink type → Add flavor → Copy ordering script!</p>
              </div>
            </div>
          </div>

          <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg mb-6">
            <p className="text-gray-700">
              <strong>💡 Pro Tip:</strong> Remember to log into Walmart in a separate tab before using shopping links!
            </p>
          </div>

          <p className="text-gray-600 mb-6">
            Ready to become a culinary master? Let's start cooking! 👨‍🍳👩‍🍳
          </p>
        </div>
      )
    }
  ];

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // Mark user as onboarded and go to dashboard
      localStorage.setItem(`user_${user?.id}_onboarded`, 'true');
      setCurrentScreen('dashboard');
      showNotification('🎉 Welcome to AI Chef! Ready to create amazing recipes!', 'success');
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const skipTutorial = () => {
    localStorage.setItem(`user_${user?.id}_onboarded`, 'true');
    setCurrentScreen('dashboard');
    showNotification('👋 Welcome! You can always access the tutorial from your dashboard.', 'info');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 p-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-600">Tutorial Progress</span>
            <span className="text-sm font-medium text-gray-600">
              {currentStep + 1} of {steps.length}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Tutorial Content */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="text-center mb-6">
            <h1 className="text-3xl font-bold text-gray-800">{steps[currentStep].title}</h1>
          </div>
          
          <div className="max-w-3xl mx-auto">
            {steps[currentStep].content}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            onClick={prevStep}
            disabled={currentStep === 0}
            className={`px-6 py-3 rounded-xl font-medium transition-all ${
              currentStep === 0
                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                : 'bg-gray-500 hover:bg-gray-600 text-white'
            }`}
          >
            ← Previous
          </button>

          <button
            onClick={skipTutorial}
            className="px-6 py-3 rounded-xl bg-gray-300 hover:bg-gray-400 text-gray-700 font-medium transition-all"
          >
            Skip Tutorial
          </button>

          <button
            onClick={nextStep}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-medium transition-all"
          >
            {currentStep === steps.length - 1 ? 'Start Cooking! 🍳' : 'Next →'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default WelcomeOnboarding;