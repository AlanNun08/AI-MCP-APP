import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import StarbucksGeneratorScreen from './components/StarbucksGeneratorScreen';
import WelcomeOnboarding from './components/WelcomeOnboarding';
import TutorialScreen from './components/TutorialScreen';

function App() {
  // BUILDYOURSMARTCART - PRODUCTION VERSION
  
  // API Configuration - Debug version
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
  
  // Debug logging for environment variables
  console.log('🔧 Environment Debug:');
  console.log('  REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
  console.log('  NODE_ENV:', process.env.NODE_ENV);
  console.log('  API URL being used:', API);
  console.log('  All REACT_APP vars:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP_')));

  // Simple cache clearing (no excessive logging) - ONLY CLEAR CACHES, NOT AUTH DATA
  useEffect(() => {
    const clearCaches = async () => {
      try {
        // Clear service worker caches AGGRESSIVELY
        if ('caches' in window) {
          const cacheNames = await caches.keys();
          console.log('🧹 Clearing caches:', cacheNames);
          await Promise.all(
            cacheNames.map(cacheName => {
              console.log('🧹 Deleting cache:', cacheName);
              return caches.delete(cacheName);
            })
          );
        }
        
        // Force reload if we detect old environment variables
        const backendUrl = process.env.REACT_APP_BACKEND_URL;
        if (backendUrl === 'https://recipe-cart-app-1.emergent.host') {
          console.log('🚨 DETECTED OLD BACKEND URL - FORCING HARD RELOAD');
          window.location.reload(true);
          return;
        }
        
        // DON'T clear auth storage on app load - let user stay logged in
        // localStorage.removeItem('authToken');
        // localStorage.removeItem('userSession');
        // localStorage.removeItem('user_auth_data');
        
      } catch (error) {
        // Silent error handling
        console.error('Cache clearing error:', error);
      }
    };
    
    // Clear caches once on app load
    clearCaches();
  }, []);

  const [currentScreen, setCurrentScreen] = useState('landing');
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [userRecipes, setUserRecipes] = useState([]);
  const [loadingRecipes, setLoadingRecipes] = useState(false);
  const [generatingRecipe, setGeneratingRecipe] = useState(false);
  const [notification, setNotification] = useState(null);
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState(null);
  const [pendingResetEmail, setPendingResetEmail] = useState(null);
  const [isLoadingAuth, setIsLoadingAuth] = useState(true);

  // Load user session from localStorage on app start - PRODUCTION FIX
  useEffect(() => {
    const loadUserSession = () => {
      try {
        const savedUser = localStorage.getItem('ai_chef_user');
        if (savedUser) {
          const userData = JSON.parse(savedUser);
          console.log('🔄 Restoring user session:', userData.email);
          setUser(userData);
          // Only set to dashboard if we're on landing page or if currentScreen is a protected route
          if (currentScreen === 'landing' || !['landing', 'register', 'verify-email', 'login', 'forgot-password', 'reset-password'].includes(currentScreen)) {
            console.log('📱 Setting screen to dashboard after session restore');
            setCurrentScreen('dashboard');
          }
        } else {
          console.log('📱 No saved user session found');
        }
      } catch (error) {
        console.error('❌ Failed to restore user session:', error);
        localStorage.removeItem('ai_chef_user');
      } finally {
        setIsLoadingAuth(false);
      }
    };
    
    // Load user session after a short delay to ensure cache clearing is done
    const timer = setTimeout(loadUserSession, 100);
    return () => clearTimeout(timer);
  }, []); // Only run once on mount

  // Monitor user state changes and save to localStorage
  useEffect(() => {
    if (user) {
      try {
        localStorage.setItem('ai_chef_user', JSON.stringify(user));
        console.log('💾 User session saved:', user.email);
      } catch (error) {
        console.error('❌ Failed to save user session:', error);
      }
    }
  }, [user]); // Save whenever user changes

  // Clear user session from localStorage
  const clearUserSession = () => {
    try {
      localStorage.removeItem('ai_chef_user');
      console.log('User session cleared');
    } catch (error) {
      console.error('Failed to clear user session:', error);
    }
  };

  // Check if user has completed onboarding
  const checkOnboardingStatus = () => {
    if (user?.id) {
      const isOnboarded = localStorage.getItem(`user_${user.id}_onboarded`);
      return isOnboarded === 'true';
    }
    return false;
  };

  // Show onboarding for new users
  useEffect(() => {
    if (user && !checkOnboardingStatus() && currentScreen === 'dashboard') {
      setCurrentScreen('welcome-onboarding');
    }
  }, [user, currentScreen]);

  // Debug logging for user state changes
  // Debug user state changes (for development only)
  useEffect(() => {
    if (user) {
      console.log('✅ User logged in:', user.email, 'Screen:', currentScreen);
    }
  }, [user, currentScreen]);

  // Notification system
  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Landing Screen Component
  const LandingScreen = () => {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 via-red-50 to-pink-50 p-4">
        <div className="max-w-6xl mx-auto">
          
          {/* Hero Section */}
          <div className="text-center py-16">
            <div className="mb-8">
              <div className="text-8xl mb-4">👨‍🍳</div>
              <h1 className="text-5xl md:text-6xl font-bold text-gray-800 mb-4">
                Welcome to <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-red-500">AI Chef</span>
              </h1>
              <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
                Your personal cooking assistant that creates custom recipes, generates viral Starbucks drinks, and builds automatic shopping lists!
              </p>
            </div>

            {/* Feature Highlights */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
              <div className="bg-white rounded-2xl shadow-lg p-8 transform hover:scale-105 transition-all duration-300">
                <div className="text-4xl mb-4">🍳</div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">AI Recipe Generator</h3>
                <p className="text-gray-600">Create personalized recipes with automatic Walmart shopping lists</p>
              </div>
              <div className="bg-white rounded-2xl shadow-lg p-8 transform hover:scale-105 transition-all duration-300">
                <div className="text-4xl mb-4">☕</div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Starbucks Secret Menu</h3>
                <p className="text-gray-600">Generate viral TikTok drink hacks with drive-thru ordering scripts</p>
              </div>
              <div className="bg-white rounded-2xl shadow-lg p-8 transform hover:scale-105 transition-all duration-300">
                <div className="text-4xl mb-4">🛒</div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">Smart Shopping</h3>
                <p className="text-gray-600">One-click Walmart integration for all your ingredients</p>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={() => setCurrentScreen('register')}
                className="bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold py-4 px-8 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 text-lg"
              >
                🚀 Start Cooking for Free
              </button>
              <button
                onClick={() => setCurrentScreen('login')}
                className="bg-gray-600 hover:bg-gray-700 text-white font-bold py-4 px-8 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 text-lg"
              >
                🔑 Sign In
              </button>
            </div>
          </div>

          {/* How It Works */}
          <div className="bg-white rounded-3xl shadow-xl p-8 md:p-12 mb-16">
            <h2 className="text-3xl font-bold text-gray-800 text-center mb-12">How AI Chef Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
              
              {/* Recipe Flow */}
              <div>
                <h3 className="text-2xl font-bold text-orange-600 mb-6 flex items-center">
                  <span className="mr-3">🍳</span>
                  Recipe Magic
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <span className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-1">1</span>
                    <div>
                      <h4 className="font-semibold text-gray-800">Choose Your Style</h4>
                      <p className="text-gray-600 text-sm">Pick from Cuisine, Snacks, or Beverages</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-1">2</span>
                    <div>
                      <h4 className="font-semibold text-gray-800">AI Creates Your Recipe</h4>
                      <p className="text-gray-600 text-sm">Personalized with your preferences and dietary needs</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="w-8 h-8 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-1">3</span>
                    <div>
                      <h4 className="font-semibold text-gray-800">Shop with One Click</h4>
                      <p className="text-gray-600 text-sm">Automatic Walmart cart with all ingredients</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Starbucks Flow */}
              <div>
                <h3 className="text-2xl font-bold text-green-600 mb-6 flex items-center">
                  <span className="mr-3">☕</span>
                  Starbucks Hacks
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-1">1</span>
                    <div>
                      <h4 className="font-semibold text-gray-800">Pick Your Vibe</h4>
                      <p className="text-gray-600 text-sm">Frappuccino, Refresher, Lemonade, or Surprise Me!</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-1">2</span>
                    <div>
                      <h4 className="font-semibold text-gray-800">Get Your Secret Drink</h4>
                      <p className="text-gray-600 text-sm">Unique creations with viral potential</p>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-bold mr-4 mt-1">3</span>
                    <div>
                      <h4 className="font-semibold text-gray-800">Order Like a Pro</h4>
                      <p className="text-gray-600 text-sm">Perfect drive-thru script ready to use</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Social Proof */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-800 mb-8">Join the AI Chef Community</h2>
            <div className="flex flex-wrap justify-center gap-4 text-2xl mb-8">
              <span>🍕</span><span>🥗</span><span>🍜</span><span>🧋</span><span>☕</span><span>🍰</span><span>🍱</span><span>🥙</span>
            </div>
            <p className="text-xl text-gray-600 mb-8">
              Ready to transform your cooking and coffee game? Let's get started! 🚀
            </p>
          </div>
        </div>
      </div>
    );
  };

  // Enhanced Registration Screen Component
  const RegisterScreen = () => {
    const [formData, setFormData] = useState({
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      confirmPassword: '',
      dietary_preferences: [],
      allergies: [],
      favorite_cuisines: []
    });
    const [isCreating, setIsCreating] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const dietaryOptions = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo'];
    const allergyOptions = ['nuts', 'shellfish', 'eggs', 'dairy', 'soy', 'wheat'];
    const cuisineOptions = ['italian', 'mexican', 'chinese', 'indian', 'mediterranean', 'american'];

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      // Validation
      if (!formData.first_name || !formData.last_name || !formData.email || !formData.password) {
        showNotification('❌ Please fill in all required fields', 'error');
        return;
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        showNotification('❌ Please enter a valid email address', 'error');
        return;
      }

      // Password validation
      if (formData.password.length < 6) {
        showNotification('❌ Password must be at least 6 characters', 'error');
        return;
      }

      if (formData.password !== formData.confirmPassword) {
        showNotification('❌ Passwords do not match', 'error');
        return;
      }

      setIsCreating(true);
      try {
        const registrationData = {
          first_name: formData.first_name,
          last_name: formData.last_name,
          email: formData.email,
          password: formData.password,
          dietary_preferences: formData.dietary_preferences,
          allergies: formData.allergies,
          favorite_cuisines: formData.favorite_cuisines
        };

        const response = await axios.post(`${API}/api/auth/register`, registrationData);
        
        setPendingVerificationEmail(formData.email);
        setCurrentScreen('verify-email');
        showNotification('✅ Registration successful! Check your email for verification code', 'success');
        
      } catch (error) {
        console.error('Registration failed:', error);
        const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
        showNotification(`❌ ${errorMessage}`, 'error');
      } finally {
        setIsCreating(false);
      }
    };

    const toggleArrayItem = (array, item, setField) => {
      const newArray = array.includes(item)
        ? array.filter(i => i !== item)
        : [...array, item];
      setField(newArray);
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md max-h-[90vh] overflow-y-auto">
          <div className="text-center mb-6">
            <div className="text-4xl mb-2">👨‍🍳</div>
            <h2 className="text-2xl font-bold text-gray-800">Create Your Account</h2>
            <p className="text-gray-600">Join AI Chef today!</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name Fields */}
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name *</label>
                <input
                  type="text"
                  placeholder="John"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name *</label>
                <input
                  type="text"
                  placeholder="Doe"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
                  required
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address *</label>
              <input
                type="email"
                placeholder="john.doe@example.com"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
                required
              />
            </div>

            {/* Password Fields */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="At least 6 characters"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password *</label>
              <input
                type="password"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm"
                required
              />
            </div>

            {/* Dietary Preferences */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Dietary Preferences</label>
              <div className="grid grid-cols-2 gap-1">
                {dietaryOptions.map(option => (
                  <label key={option} className="flex items-center space-x-2 p-1 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.dietary_preferences.includes(option)}
                      onChange={() => toggleArrayItem(formData.dietary_preferences, option, 
                        (newArray) => setFormData({...formData, dietary_preferences: newArray}))}
                      className="rounded text-green-500"
                    />
                    <span className="text-xs capitalize">{option}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Allergies */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Allergies</label>
              <div className="grid grid-cols-2 gap-1">
                {allergyOptions.map(option => (
                  <label key={option} className="flex items-center space-x-2 p-1 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.allergies.includes(option)}
                      onChange={() => toggleArrayItem(formData.allergies, option, 
                        (newArray) => setFormData({...formData, allergies: newArray}))}
                      className="rounded text-red-500"
                    />
                    <span className="text-xs capitalize">{option}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Favorite Cuisines */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Favorite Cuisines</label>
              <div className="grid grid-cols-2 gap-1">
                {cuisineOptions.map(option => (
                  <label key={option} className="flex items-center space-x-2 p-1 rounded-lg hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.favorite_cuisines.includes(option)}
                      onChange={() => toggleArrayItem(formData.favorite_cuisines, option, 
                        (newArray) => setFormData({...formData, favorite_cuisines: newArray}))}
                      className="rounded text-blue-500"
                    />
                    <span className="text-xs capitalize">{option}</span>
                  </label>
                ))}
              </div>
            </div>

            <button
              type="submit"
              disabled={isCreating}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-3 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {isCreating ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Creating Account...</span>
                </div>
              ) : (
                '✨ Create Account'
              )}
            </button>
          </form>

          <button
            onClick={() => setCurrentScreen('landing')}
            className="w-full mt-4 text-gray-600 hover:text-gray-800 transition-colors text-sm"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  };

  // Email Verification Screen Component
  const EmailVerificationScreen = () => {
    const [verificationCode, setVerificationCode] = useState('');
    const [isVerifying, setIsVerifying] = useState(false);
    const [isResending, setIsResending] = useState(false);
    const [timeRemaining, setTimeRemaining] = useState(300); // 5 minutes in seconds

    // Countdown timer
    useEffect(() => {
      if (timeRemaining > 0) {
        const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
        return () => clearTimeout(timer);
      }
    }, [timeRemaining]);

    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handleVerify = async (e) => {
      e.preventDefault();
      
      if (!verificationCode || verificationCode.length !== 6) {
        showNotification('❌ Please enter a 6-digit verification code', 'error');
        return;
      }

      setIsVerifying(true);
      try {
        const response = await axios.post(`${API}/api/auth/verify`, {
          email: pendingVerificationEmail,
          code: verificationCode
        });

        setUser(response.data.user);
        setCurrentScreen('dashboard');
        showNotification('🎉 Email verified successfully! Welcome to AI Chef!', 'success');
        
      } catch (error) {
        console.error('Verification failed:', error);
        const errorMessage = error.response?.data?.detail || 'Verification failed. Please try again.';
        showNotification(`❌ ${errorMessage}`, 'error');
      } finally {
        setIsVerifying(false);
      }
    };

    const handleResendCode = async () => {
      setIsResending(true);
      try {
        await axios.post(`${API}/api/auth/resend-code`, {
          email: pendingVerificationEmail
        });

        setTimeRemaining(300); // Reset timer
        setVerificationCode(''); // Clear current code
        showNotification('📧 New verification code sent!', 'success');
        
      } catch (error) {
        console.error('Resend failed:', error);
        const errorMessage = error.response?.data?.detail || 'Failed to resend code. Please try again.';
        showNotification(`❌ ${errorMessage}`, 'error');
      } finally {
        setIsResending(false);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4">📧</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-2">Check Your Email</h2>
            <p className="text-gray-600 text-sm">
              We sent a 6-digit verification code to<br/>
              <strong>{pendingVerificationEmail}</strong>
            </p>
          </div>

          <form onSubmit={handleVerify} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3 text-center">
                Enter Verification Code
              </label>
              <input
                type="text"
                placeholder="123456"
                value={verificationCode}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                  setVerificationCode(value);
                }}
                className="w-full px-4 py-4 text-center text-2xl font-mono border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent tracking-widest"
                maxLength={6}
                autoComplete="one-time-code"
                autoFocus
              />
              <div className="text-center mt-3">
                {timeRemaining > 0 ? (
                  <p className="text-sm text-gray-500">
                    Code expires in: <span className="font-mono text-red-500">{formatTime(timeRemaining)}</span>
                  </p>
                ) : (
                  <p className="text-sm text-red-500">Code has expired</p>
                )}
              </div>
            </div>

            <button
              type="submit"
              disabled={isVerifying || verificationCode.length !== 6}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {isVerifying ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Verifying...</span>
                </div>
              ) : (
                '✅ Verify Email'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 mb-3">Didn't receive the code?</p>
            <button
              onClick={handleResendCode}
              disabled={isResending || timeRemaining > 240} // Allow resend after 1 minute
              className="text-blue-600 hover:text-blue-800 font-medium text-sm underline disabled:text-gray-400 disabled:no-underline"
            >
              {isResending ? (
                <span className="flex items-center justify-center space-x-1">
                  <div className="w-3 h-3 border border-blue-600 border-t-transparent rounded-full animate-spin"></div>
                  <span>Sending...</span>
                </span>
              ) : timeRemaining > 240 ? (
                `Resend available in ${formatTime(timeRemaining - 240)}`
              ) : (
                '📤 Resend Code'
              )}
            </button>
          </div>

          <button
            onClick={() => {
              setCurrentScreen('register');
              setPendingVerificationEmail(null);
            }}
            className="w-full mt-6 text-gray-600 hover:text-gray-800 transition-colors text-sm"
          >
            ← Back to Registration
          </button>
        </div>
      </div>
    );
  };

  // Enhanced Login Screen Component
  const LoginScreen = () => {
    const [formData, setFormData] = useState({
      email: '',
      password: ''
    });
    const [isLoggingIn, setIsLoggingIn] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      if (!formData.email || !formData.password) {
        showNotification('❌ Please enter both email and password', 'error');
        return;
      }

      setIsLoggingIn(true);
      try {
        const response = await axios.post(`${API}/api/auth/login`, formData);
        
        // Check if user is unverified
        if (response.data.status === 'unverified' && response.data.needs_verification) {
          setPendingVerificationEmail(response.data.email);
          setCurrentScreen('verify-email');
          showNotification('📧 Please verify your email to continue', 'error');
          return;
        }
        
        // Successful login
        if (response.data.status === 'success') {
          setUser(response.data.user);
          setCurrentScreen('dashboard');
          
          // Mark user as onboarded to skip tutorial for returning users
          localStorage.setItem(`user_${response.data.user.id}_onboarded`, 'true');
          
          showNotification(`🎉 Welcome back, ${response.data.user.first_name}!`, 'success');
        }
        
      } catch (error) {
        console.error('Login failed:', error);
        const errorMessage = error.response?.data?.detail || 'Login failed. Please check your credentials.';
        showNotification(`❌ ${errorMessage}`, 'error');
      } finally {
        setIsLoggingIn(false);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="text-4xl mb-2">👨‍🍳</div>
            <h2 className="text-2xl font-bold text-gray-800">Welcome Back</h2>
            <p className="text-gray-600">Sign in to your account</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                placeholder="john.doe@example.com"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoggingIn}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {isLoggingIn ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Signing In...</span>
                </div>
              ) : (
                '🔑 Sign In'
              )}
            </button>
          </form>

          <div className="mt-6 text-center space-y-3">
            <button
              onClick={() => setCurrentScreen('forgot-password')}
              className="text-sm text-blue-600 hover:text-blue-800 font-medium underline"
            >
              🔒 Forgot your password?
            </button>
            
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <button
                onClick={() => setCurrentScreen('register')}
                className="text-blue-600 hover:text-blue-800 font-medium underline"
              >
                Sign up here
              </button>
            </p>
          </div>

          <button
            onClick={() => setCurrentScreen('landing')}
            className="w-full mt-4 text-gray-600 hover:text-gray-800 transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  };

  // Enhanced Dashboard Screen Component
  const DashboardScreen = () => (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-md mx-auto">
        <div className="bg-white rounded-2xl shadow-sm p-6 mb-4">
          <div className="flex items-center space-x-3 mb-6">
            <div className="text-3xl">👨‍🍳</div>
            <div>
              <h2 className="text-xl font-bold text-gray-800">Hi, {user?.first_name}!</h2>
              <p className="text-gray-600 text-sm">Ready to cook something amazing?</p>
              {user?.is_verified && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 mt-1">
                  ✅ Verified
                </span>
              )}
            </div>
          </div>
          
          <div className="space-y-3">
            <button
              onClick={() => setCurrentScreen('generate-recipe')}
              className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 active:scale-95"
            >
              🎯 Generate AI Recipe
            </button>
            
            <button
              onClick={() => setCurrentScreen('starbucks-generator')}
              className="w-full bg-gradient-to-br from-green-500 to-green-600 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 active:scale-95"
            >
              ☕ Starbucks Secret Menu
            </button>
            
            <button
              onClick={() => setCurrentScreen('tutorial')}
              className="w-full bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 active:scale-95"
            >
              📚 How to Use AI Chef
            </button>
            
            <button
              onClick={() => setCurrentScreen('all-recipes')}
              className="w-full bg-purple-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 active:scale-95"
            >
              📚 Recipe History
            </button>
          </div>
        </div>
        
        {/* Quick Stats */}
        <div className="bg-gradient-to-r from-green-100 to-blue-100 rounded-2xl p-4 mb-4">
          <h3 className="font-semibold text-gray-800 mb-2">🌟 Welcome to AI Chef!</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <p>• Generate personalized recipes with AI</p>
            <p>• Instant Walmart grocery delivery</p>
            <p>• Healthy & budget-friendly options</p>
          </div>
        </div>
        
        {/* Logout Button */}
        <button
          onClick={() => {
            setUser(null);
            clearUserSession(); // Clear localStorage
            setPendingVerificationEmail(null);
            setCurrentScreen('landing');
            showNotification('👋 Signed out successfully', 'success');
          }}
          className="w-full text-gray-500 hover:text-gray-700 transition-colors py-2"
        >
          🚪 Sign Out
        </button>
      </div>
    </div>
  );

  // Forgot Password Screen Component
  const ForgotPasswordScreen = () => {
    const [email, setEmail] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      if (!email) {
        showNotification('❌ Please enter your email address', 'error');
        return;
      }

      // Email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        showNotification('❌ Please enter a valid email address', 'error');
        return;
      }

      setIsSubmitting(true);
      try {
        await axios.post(`${API}/api/auth/forgot-password`, { email });
        
        setPendingResetEmail(email);
        setCurrentScreen('reset-password');
        showNotification('📧 Password reset code sent! Check your email', 'success');
        
      } catch (error) {
        console.error('Password reset request failed:', error);
        // Don't show specific error for security - always show success message
        setPendingResetEmail(email);
        setCurrentScreen('reset-password');
        showNotification('📧 If an account exists, a reset code has been sent', 'success');
      } finally {
        setIsSubmitting(false);
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="text-4xl mb-2">🔒</div>
            <h2 className="text-2xl font-bold text-gray-800">Forgot Password?</h2>
            <p className="text-gray-600">No worries! We'll send you a reset code</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
              <input
                type="email"
                placeholder="Enter your email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-gradient-to-r from-red-500 to-orange-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {isSubmitting ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Sending Reset Code...</span>
                </div>
              ) : (
                '📧 Send Reset Code'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600">
              Remember your password?{' '}
              <button
                onClick={() => setCurrentScreen('login')}
                className="text-blue-600 hover:text-blue-800 font-medium underline"
              >
                Sign in here
              </button>
            </p>
          </div>

          <button
            onClick={() => setCurrentScreen('landing')}
            className="w-full mt-4 text-gray-600 hover:text-gray-800 transition-colors"
          >
            ← Back to Home
          </button>
        </div>
      </div>
    );
  };

  // Reset Password Screen Component
  const ResetPasswordScreen = () => {
    const [formData, setFormData] = useState({
      resetCode: '',
      newPassword: '',
      confirmPassword: ''
    });
    const [isResetting, setIsResetting] = useState(false);
    const [showPasswords, setShowPasswords] = useState(false);
    const [timeRemaining, setTimeRemaining] = useState(600); // 10 minutes

    // Countdown timer
    useEffect(() => {
      if (timeRemaining > 0) {
        const timer = setTimeout(() => setTimeRemaining(timeRemaining - 1), 1000);
        return () => clearTimeout(timer);
      }
    }, [timeRemaining]);

    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60);
      const secs = seconds % 60;
      return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      if (!formData.resetCode || !formData.newPassword || !formData.confirmPassword) {
        showNotification('❌ Please fill in all fields', 'error');
        return;
      }

      if (formData.resetCode.length !== 6) {
        showNotification('❌ Please enter a 6-digit reset code', 'error');
        return;
      }

      if (formData.newPassword.length < 6) {
        showNotification('❌ Password must be at least 6 characters', 'error');
        return;
      }

      if (formData.newPassword !== formData.confirmPassword) {
        showNotification('❌ Passwords do not match', 'error');
        return;
      }

      setIsResetting(true);
      try {
        await axios.post(`${API}/api/auth/reset-password`, {
          email: pendingResetEmail,
          reset_code: formData.resetCode,
          new_password: formData.newPassword
        });
        
        setCurrentScreen('login');
        showNotification('✅ Password reset successful! Please login with your new password', 'success');
        
      } catch (error) {
        console.error('Password reset failed:', error);
        const errorMessage = error.response?.data?.detail || 'Password reset failed. Please try again.';
        showNotification(`❌ ${errorMessage}`, 'error');
      } finally {
        setIsResetting(false);
      }
    };

    const handleResendCode = async () => {
      try {
        await axios.post(`${API}/api/auth/forgot-password`, { email: pendingResetEmail });
        setTimeRemaining(600); // Reset timer
        setFormData({...formData, resetCode: ''}); // Clear current code
        showNotification('📧 New reset code sent!', 'success');
      } catch (error) {
        showNotification('📧 If an account exists, a new reset code has been sent', 'success');
      }
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md">
          <div className="text-center mb-8">
            <div className="text-4xl mb-2">🔑</div>
            <h2 className="text-2xl font-bold text-gray-800">Reset Password</h2>
            <p className="text-gray-600 text-sm">
              Enter the 6-digit code sent to<br/>
              <strong>{pendingResetEmail}</strong>
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 text-center">
                Reset Code
              </label>
              <input
                type="text"
                placeholder="123456"
                value={formData.resetCode}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '').slice(0, 6);
                  setFormData({...formData, resetCode: value});
                }}
                className="w-full px-4 py-3 text-center text-xl font-mono border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent tracking-widest"
                maxLength={6}
                autoComplete="one-time-code"
              />
              <div className="text-center mt-2">
                {timeRemaining > 0 ? (
                  <p className="text-sm text-gray-500">
                    Code expires in: <span className="font-mono text-red-500">{formatTime(timeRemaining)}</span>
                  </p>
                ) : (
                  <p className="text-sm text-red-500">Code has expired</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">New Password</label>
              <div className="relative">
                <input
                  type={showPasswords ? "text" : "password"}
                  placeholder="Enter new password (min 6 characters)"
                  value={formData.newPassword}
                  onChange={(e) => setFormData({...formData, newPassword: e.target.value})}
                  className="w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  required
                  minLength={6}
                />
                <button
                  type="button"
                  onClick={() => setShowPasswords(!showPasswords)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700"
                >
                  {showPasswords ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Confirm New Password</label>
              <input
                type={showPasswords ? "text" : "password"}
                placeholder="Confirm your new password"
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent"
                required
              />
            </div>

            <button
              type="submit"
              disabled={isResetting || formData.resetCode.length !== 6}
              className="w-full bg-gradient-to-r from-red-500 to-orange-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
            >
              {isResetting ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Resetting Password...</span>
                </div>
              ) : (
                '🔑 Reset Password'
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 mb-3">Didn't receive the code?</p>
            <button
              onClick={handleResendCode}
              disabled={timeRemaining > 540} // Allow resend after 1 minute
              className="text-blue-600 hover:text-blue-800 font-medium text-sm underline disabled:text-gray-400 disabled:no-underline"
            >
              {timeRemaining > 540 ? (
                `Resend available in ${formatTime(timeRemaining - 540)}`
              ) : (
                '📤 Resend Reset Code'
              )}
            </button>
          </div>

          <button
            onClick={() => {
              setCurrentScreen('login');
              setPendingResetEmail(null);
            }}
            className="w-full mt-6 text-gray-600 hover:text-gray-800 transition-colors text-sm"
          >
            ← Back to Login
          </button>
        </div>
      </div>
    );
  };

  // Recipe Generation Screen Component
  const RecipeGenerationScreen = () => {
    const [formData, setFormData] = useState({
      recipe_type: '', // 'cuisine', 'snack', or 'beverage'
      cuisine_type: '',
      snack_type: '',
      beverage_type: '',
      dietary_preferences: [],
      ingredients_on_hand: '',
      prep_time_max: '',
      servings: 4,
      difficulty: 'medium',
      is_healthy: false,
      max_calories_per_serving: 400,
      is_budget_friendly: false,
      max_budget: 20
    });
    const [isGenerating, setIsGenerating] = useState(false);

    const cuisineOptions = ['italian', 'mexican', 'chinese', 'indian', 'mediterranean', 'american', 'thai', 'japanese', 'french', 'korean'];
    const snackOptions = ['acai bowls', 'fruit lemon slices chili', 'frozen yogurt berry bites'];
    const beverageOptions = ['boba tea', 'thai tea', 'special lemonades'];
    const dietaryOptions = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo'];
    const difficultyOptions = ['easy', 'medium', 'hard'];

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      console.log('🚀 =================================');
      console.log('🚀 RECIPE GENERATION FORM SUBMITTED');
      console.log('🚀 =================================');
      console.log('🔍 Form submission event:', e);
      console.log('🔍 Current form data:', formData);
      console.log('🔍 Current user:', user);
      console.log('🔍 Timestamp:', new Date().toISOString());
      
      // Validate that a recipe type and specific type are selected
      if (!formData.recipe_type) {
        console.log('❌ Validation failed: No recipe type selected');
        showNotification('❌ Please select a recipe category (Cuisine, Snack, or Beverage)', 'error');
        return;
      }

      let selectedType = '';
      if (formData.recipe_type === 'cuisine' && !formData.cuisine_type) {
        console.log('❌ Validation failed: No cuisine type selected');
        showNotification('❌ Please select a cuisine type', 'error');
        return;
      } else if (formData.recipe_type === 'snack' && !formData.snack_type) {
        console.log('❌ Validation failed: No snack type selected');
        showNotification('❌ Please select a snack type', 'error');
        return;
      } else if (formData.recipe_type === 'beverage' && !formData.beverage_type) {
        console.log('❌ Validation failed: No beverage type selected');
        showNotification('❌ Please select a beverage type', 'error');
        return;
      }

      console.log('✅ Form validation passed');

      // Determine the final type for the API
      if (formData.recipe_type === 'cuisine') {
        selectedType = formData.cuisine_type;
      } else if (formData.recipe_type === 'snack') {
        selectedType = formData.snack_type;
      } else if (formData.recipe_type === 'beverage') {
        selectedType = formData.beverage_type;
      }

      console.log('🔍 Selected type determined:', selectedType);
      console.log('🔍 Recipe type:', formData.recipe_type);

      setIsGenerating(true);
      console.log('🔍 Set isGenerating to true - UI should show loading state');
      
      try {
        const requestData = {
          user_id: user.id,
          recipe_category: formData.recipe_type, // 'cuisine', 'snack', or 'beverage'
          cuisine_type: selectedType,
          dietary_preferences: formData.dietary_preferences,
          ingredients_on_hand: formData.ingredients_on_hand ? formData.ingredients_on_hand.split(',').map(i => i.trim()) : [],
          prep_time_max: formData.prep_time_max ? parseInt(formData.prep_time_max) : null,
          servings: formData.servings,
          difficulty: formData.difficulty,
          is_healthy: formData.is_healthy,
          max_calories_per_serving: formData.is_healthy ? formData.max_calories_per_serving : null,
          is_budget_friendly: formData.is_budget_friendly,
          max_budget: formData.is_budget_friendly ? formData.max_budget : null
        };

        console.log('🚀 =================================');
        console.log('🚀 RECIPE GENERATION - OPENAI CALL');
        console.log('🚀 =================================');
        console.log('🔍 REQUEST DATA:', requestData);
        console.log('🔍 API URL:', `${API}/api/recipes/generate`);
        console.log('🔍 USER:', user);
        console.log('🔍 FORM DATA:', formData);

        const response = await axios.post(`${API}/api/recipes/generate`, requestData);
        
        console.log('🚀 =================================');
        console.log('🚀 RECIPE GENERATION - RESPONSE RECEIVED');
        console.log('🚀 =================================');
        console.log('✅ Recipe generation response:', response.data);
        console.log('🔍 Response status:', response.status);
        console.log('🔍 Recipe ID:', response.data?.id);
        console.log('🔍 Recipe title:', response.data?.title);
        console.log('🔍 Recipe shopping_list:', response.data?.shopping_list);
        console.log('🔍 Recipe ingredients:', response.data?.ingredients);
        console.log('🔍 Recipe instructions:', response.data?.instructions);
        
        // Store recipe and navigate to detail
        window.currentRecipe = response.data;
        console.log('🔍 Stored in window.currentRecipe:', window.currentRecipe);
        
        setCurrentScreen('recipe-detail');
        console.log('🔍 Navigating to recipe-detail screen');
        
        showNotification('🎉 Recipe generated successfully!', 'success');
        
      } catch (error) {
        console.error('Recipe generation failed:', error);
        const errorMessage = error.response?.data?.detail || 'Failed to generate recipe. Please try again.';
        showNotification(`❌ ${errorMessage}`, 'error');
      } finally {
        setIsGenerating(false);
      }
    };

    const toggleArrayItem = (array, item, setField) => {
      const newArray = array.includes(item)
        ? array.filter(i => i !== item)
        : [...array, item];
      setField(newArray);
    };

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto">
          <div className="bg-white rounded-2xl shadow-sm p-6 mb-4">
            <div className="flex items-center space-x-3 mb-6">
              <button
                onClick={() => setCurrentScreen('dashboard')}
                className="text-gray-600 hover:text-gray-800"
              >
                ← Back
              </button>
              <div>
                <h2 className="text-xl font-bold text-gray-800">🤖 Generate AI Recipe</h2>
                <p className="text-gray-600 text-sm">Create a personalized recipe just for you</p>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Recipe Category Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Recipe Category *</label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Cuisine Card */}
                  <div 
                    className={`border-2 rounded-xl p-4 cursor-pointer transition-all duration-200 ${
                      formData.recipe_type === 'cuisine' 
                        ? 'border-green-500 bg-green-50' 
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                    onClick={() => setFormData({...formData, recipe_type: 'cuisine', snack_type: '', beverage_type: ''})}
                  >
                    <div className="text-center">
                      <div className="text-3xl mb-2">🍝</div>
                      <h3 className="font-bold text-gray-800">Cuisine</h3>
                      <p className="text-xs text-gray-600">Traditional dishes from around the world</p>
                    </div>
                  </div>

                  {/* Snacks Card */}
                  <div 
                    className={`border-2 rounded-xl p-4 cursor-pointer transition-all duration-200 ${
                      formData.recipe_type === 'snack' 
                        ? 'border-green-500 bg-green-50' 
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                    onClick={() => setFormData({...formData, recipe_type: 'snack', cuisine_type: '', beverage_type: ''})}
                  >
                    <div className="text-center">
                      <div className="text-3xl mb-2">🍪</div>
                      <h3 className="font-bold text-gray-800">Snacks</h3>
                      <p className="text-xs text-gray-600">Healthy bowls, treats, and bite-sized delights</p>
                    </div>
                  </div>

                  {/* Beverages Card */}
                  <div 
                    className={`border-2 rounded-xl p-4 cursor-pointer transition-all duration-200 ${
                      formData.recipe_type === 'beverage' 
                        ? 'border-green-500 bg-green-50' 
                        : 'border-gray-200 hover:border-green-300'
                    }`}
                    onClick={() => setFormData({...formData, recipe_type: 'beverage', cuisine_type: '', snack_type: ''})}
                  >
                    <div className="text-center">
                      <div className="text-3xl mb-2">🧋</div>
                      <h3 className="font-bold text-gray-800">Beverages</h3>
                      <p className="text-xs text-gray-600">Boba, tea, and specialty drinks</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Specific Type Selection */}
              {formData.recipe_type === 'cuisine' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Cuisine Type *</label>
                  <select
                    value={formData.cuisine_type}
                    onChange={(e) => setFormData({...formData, cuisine_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select cuisine...</option>
                    {cuisineOptions.map(cuisine => (
                      <option key={cuisine} value={cuisine}>
                        {cuisine.charAt(0).toUpperCase() + cuisine.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {formData.recipe_type === 'snack' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Snack Type *</label>
                  <select
                    value={formData.snack_type}
                    onChange={(e) => setFormData({...formData, snack_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    required
                  >
                    <option value="">Select snack type...</option>
                    {snackOptions.map(snack => (
                      <option key={snack} value={snack}>
                        {snack.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {formData.recipe_type === 'beverage' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Beverage Type *</label>
                  <select
                    value={formData.beverage_type}
                    onChange={(e) => setFormData({...formData, beverage_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    required
                    data-testid="beverage-type-select"
                  >
                    <option value="">Select beverage type...</option>
                    {beverageOptions.map(beverage => (
                      <option key={beverage} value={beverage}>
                        {beverage.split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Dietary Preferences */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Dietary Preferences</label>
                <div className="grid grid-cols-2 gap-2">
                  {dietaryOptions.map(option => (
                    <label key={option} className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-50 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.dietary_preferences.includes(option)}
                        onChange={() => toggleArrayItem(formData.dietary_preferences, option, 
                          (newArray) => setFormData({...formData, dietary_preferences: newArray}))}
                        className="rounded text-green-500"
                      />
                      <span className="text-sm capitalize">{option}</span>
                    </label>
                  ))}
                </div>
              </div>

              {/* Healthy Mode Toggle */}
              <div className="bg-green-50 p-4 rounded-xl">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_healthy}
                    onChange={(e) => setFormData({...formData, is_healthy: e.target.checked})}
                    className="rounded text-green-500"
                  />
                  <div>
                    <span className="font-medium text-green-800">🍃 Healthy Mode</span>
                    <p className="text-sm text-green-600">Limit calories per serving</p>
                  </div>
                </label>
                {formData.is_healthy && (
                  <div className="mt-3">
                    <label className="block text-sm font-medium text-green-700 mb-1">Max Calories per Serving</label>
                    <input
                      type="number"
                      value={formData.max_calories_per_serving}
                      onChange={(e) => setFormData({...formData, max_calories_per_serving: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500"
                      min="200"
                      max="800"
                      placeholder="400"
                    />
                  </div>
                )}
              </div>

              {/* Budget Mode Toggle */}
              <div className="bg-blue-50 p-4 rounded-xl">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_budget_friendly}
                    onChange={(e) => setFormData({...formData, is_budget_friendly: e.target.checked})}
                    className="rounded text-blue-500"
                  />
                  <div>
                    <span className="font-medium text-blue-800">💰 Budget Mode</span>
                    <p className="text-sm text-blue-600">Set maximum budget</p>
                  </div>
                </label>
                {formData.is_budget_friendly && (
                  <div className="mt-3">
                    <label className="block text-sm font-medium text-blue-700 mb-1">Max Budget ($)</label>
                    <input
                      type="number"
                      value={formData.max_budget}
                      onChange={(e) => setFormData({...formData, max_budget: parseInt(e.target.value)})}
                      className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      min="5"
                      max="100"
                      placeholder="20"
                    />
                  </div>
                )}
              </div>

              {/* Servings and Difficulty */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Servings</label>
                  <input
                    type="number"
                    value={formData.servings}
                    onChange={(e) => setFormData({...formData, servings: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    min="1"
                    max="12"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                  <select
                    value={formData.difficulty}
                    onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    data-testid="difficulty-select"
                  >
                    {difficultyOptions.map(difficulty => (
                      <option key={difficulty} value={difficulty}>
                        {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Optional Fields */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Ingredients on Hand (optional)</label>
                <input
                  type="text"
                  value={formData.ingredients_on_hand}
                  onChange={(e) => setFormData({...formData, ingredients_on_hand: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="chicken, rice, onions (comma separated)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Max Prep Time (optional)</label>
                <input
                  type="number"
                  value={formData.prep_time_max}
                  onChange={(e) => setFormData({...formData, prep_time_max: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="30 minutes"
                />
              </div>

              <button
                type="submit"
                disabled={isGenerating}
                className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
              >
                {isGenerating ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>AI is cooking up your recipe...</span>
                  </div>
                ) : (
                  '🤖 Generate Recipe'
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  };

  // Recipe Detail Screen Component - COMPLETELY NEW INGREDIENT SELECTION FOCUSED DESIGN
  const RecipeDetailScreen = ({ recipe, showBackButton = false }) => {
    console.log('🚀 =================================');
    console.log('🚀 RECIPE DETAIL SCREEN COMPONENT MOUNTED');
    console.log('🚀 =================================');
    console.log('🔍 Props received:');
    console.log('  - recipe:', recipe);
    console.log('  - showBackButton:', showBackButton);
    console.log('🔍 Component render time:', new Date().toISOString());
    
    const [productOptions, setProductOptions] = useState({}); // Store all product options per ingredient
    const [selectedProducts, setSelectedProducts] = useState({}); // Store user selections
    const [cartItems, setCartItems] = useState([]);
    const [finalWalmartUrl, setFinalWalmartUrl] = useState(null);
    const [loadingCart, setLoadingCart] = useState(false);

    // Auto-generate product options when recipe loads using real Walmart API
    useEffect(() => {
      console.log('🚀 =================================');
      console.log('🚀 RECIPE DETAIL SCREEN - useEffect TRIGGERED');
      console.log('🚀 =================================');
      console.log('🔍 RECIPE OBJECT:', recipe);
      console.log('🔍 RECIPE ID:', recipe?.id);
      console.log('🔍 RECIPE TITLE:', recipe?.title);
      console.log('🔍 RECIPE SHOPPING LIST:', recipe?.shopping_list);
      console.log('🔍 RECIPE INGREDIENTS:', recipe?.ingredients);
      console.log('🔍 USER OBJECT:', user);
      console.log('🔍 USER ID:', user?.id);
      console.log('🔍 BACKEND API URL:', API);
      console.log('🔍 ENVIRONMENT VARIABLES:', {
        REACT_APP_BACKEND_URL: process.env.REACT_APP_BACKEND_URL,
        NODE_ENV: process.env.NODE_ENV
      });
      
      if (recipe?.id && (recipe?.shopping_list?.length > 0 || recipe?.ingredients?.length > 0)) {
        console.log('✅ CONDITIONS MET - Starting cart options call');
        console.log('🔍 Recipe has ID:', !!recipe.id);
        console.log('🔍 Shopping list length:', recipe?.shopping_list?.length || 0);
        console.log('🔍 Ingredients length:', recipe?.ingredients?.length || 0);
        
        setLoadingCart(true);
        
        console.log('🚀 =================================');
        console.log('🚀 MAKING CART OPTIONS API CALL');
        console.log('🚀 =================================');
        
        const apiParams = {
          recipe_id: recipe.id,
          user_id: user?.id || 'demo_user'
        };
        
        const fullUrl = `${API}/api/grocery/cart-options`;
        
        console.log('🔍 API CALL DETAILS:');
        console.log('  - URL:', fullUrl);
        console.log('  - Params:', apiParams);
        console.log('  - Method: POST');
        console.log('  - Headers: application/json');
        
        // Call the backend API to get real Walmart product options
        axios.post(fullUrl, {}, {
          params: apiParams
        })
        .then(response => {
          console.log('✅ Cart options response:', response.data);
          console.log('🔍 DEBUG - Response status:', response.status);
          console.log('🔍 DEBUG - Response headers:', response.headers);
          console.log('🔍 DEBUG - Full response object:', response);
          
          // Handle the case where no products are found
          if (response.data && response.data.status === 'no_products_found') {
            console.log('⚠️ No Walmart products found for this recipe');
            console.log('🔍 DEBUG - No products message:', response.data.message);
            setProductOptions({});
            setSelectedProducts({});
            setCartItems([]);
            setFinalWalmartUrl('');
            return; // Exit early
          }
          
          console.log('🛒 Cart options response:', response.data);
          console.log('🔍 DEBUG - Recipe ID used:', recipe.id);
          console.log('🔍 DEBUG - User ID used:', user?.id || 'demo_user');
          console.log('🔍 DEBUG - Shopping list from recipe:', recipe.shopping_list);
          
          // Check for correct backend format: response.data.ingredient_options
          if (response.data && response.data.ingredient_options) {
            console.log('🔍 DEBUG - Ingredient options found:', response.data.ingredient_options.length);
            console.log('🔍 DEBUG - Total products:', response.data.total_products);
            
            // Store all product options per ingredient - CORRECT BACKEND FORMAT
            const options = {};
            const defaultSelections = {};
            const newCartItems = [];
            
            // Process correct format: ingredient_options array with options sub-arrays
            response.data.ingredient_options.forEach((ingredientOption, index) => {
              const ingredientName = ingredientOption.ingredient_name || ingredientOption.original_ingredient;
              console.log(`🔍 DEBUG - Processing ingredient ${index + 1}: ${ingredientName}`);
              
              // Backend uses 'options' field (not 'products')
              if (ingredientOption.options && ingredientOption.options.length > 0) {
                console.log(`🔍 DEBUG - Found ${ingredientOption.options.length} products for ${ingredientName}`);
                console.log(`🔍 DEBUG - First product:`, ingredientOption.options[0]);
                
                // Store all options for this ingredient
                options[ingredientName] = ingredientOption.options;
                
                // Default to first option
                const firstProduct = ingredientOption.options[0];
                defaultSelections[ingredientName] = firstProduct.product_id;
                
                // Add to cart with first product
                newCartItems.push({
                  name: firstProduct.name || ingredientName,
                  price: parseFloat(firstProduct.price) || 2.99,
                  quantity: 1,
                  product_id: firstProduct.product_id,
                  ingredient_name: ingredientName
                });
                
                console.log(`🔍 DEBUG - Added to cart: ${firstProduct.name} - $${firstProduct.price}`);
              } else {
                console.log(`🔍 DEBUG - No products found for ingredient: ${ingredientName}`);
              }
            });
            
            setProductOptions(options);
            setSelectedProducts(defaultSelections);
            setCartItems(newCartItems);
            
            console.log('🔍 DEBUG - Final product options:', options);
            console.log('🔍 DEBUG - Default selections:', defaultSelections);
            console.log('🔍 DEBUG - Initial cart items:', newCartItems);
            console.log('🔍 DEBUG - Cart total:', newCartItems.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2));
            
            // Generate affiliate URL with default selections
            // Generate Walmart URL with correct format using SELECTED items only
            const walmartItems = [];
            const finalQuantities = {};
            
            // Count quantities for SELECTED products only (from cartItems)
            newCartItems.forEach(item => {
              if (item.product_id) {
                const quantity = (typeof item.quantity === 'number' && item.quantity > 0) ? item.quantity : 1;
                const qty = finalQuantities[item.product_id] || 0;
                finalQuantities[item.product_id] = qty + quantity;
              }
            });
            
            console.log('🔍 DEBUG - Final quantities for URL:', finalQuantities);
            
            // Format for Walmart URL: productId or productId_quantity
            Object.entries(finalQuantities).forEach(([productId, quantity]) => {
              if (productId) {
                if (quantity === 1) {
                  walmartItems.push(productId);
                } else {
                  walmartItems.push(`${productId}_${Math.floor(quantity)}`);
                }
              }
            });
            
            if (walmartItems.length > 0) {
              const finalUrl = `https://affil.walmart.com/cart/addToCart?items=${walmartItems.join(',')}`;
              setFinalWalmartUrl(finalUrl);
              console.log('✅ Walmart URL generated with SELECTED items only:', walmartItems.length, 'items');
              console.log('🔍 DEBUG - Generated URL:', finalUrl);
              console.log('🔍 DEBUG - URL items:', walmartItems);
            } else {
              console.warn('⚠️ No selected items for Walmart URL generation');
              setFinalWalmartUrl('');
            };
            
            console.log('✅ Product options loaded:', Object.keys(options).length, 'ingredients');
          } else {
            // No valid API response - check for different formats
            console.log('⚠️ API Response Debug:', response.data);
            console.log('🔍 DEBUG - Response data keys:', Object.keys(response.data || {}));
            if (response.data && response.data.ingredients) {
              console.log('⚠️ Found ingredients format (old), expected ingredient_options format');
            } else {
              console.log('⚠️ Invalid API response - only real Walmart products are used');
            }
          }
        })
        .catch(error => {
          console.error('❌ Error fetching cart options:', error);
          console.log('🔍 DEBUG - Error details:', error.response?.data);
          console.log('🔍 DEBUG - Error status:', error.response?.status);
          console.log('🔍 DEBUG - Request URL:', `${API}/api/grocery/cart-options`);
          console.log('🔍 DEBUG - Request params:', { recipe_id: recipe.id, user_id: user?.id || 'demo_user' });
          console.log('ℹ️ No cart generated - only real Walmart products are used');
        })
        .finally(() => {
          setLoadingCart(false);
        });
      } else {
        console.log('❌ CONDITIONS NOT MET - Cart options call skipped');
        console.log('🔍 Recipe ID exists:', !!recipe?.id);
        console.log('🔍 Shopping list exists:', !!recipe?.shopping_list);
        console.log('🔍 Shopping list length:', recipe?.shopping_list?.length || 0);
        console.log('🔍 Ingredients exists:', !!recipe?.ingredients);
        console.log('🔍 Ingredients length:', recipe?.ingredients?.length || 0);
        console.log('🔍 Recipe object:', recipe);
      }
    }, [recipe, user]);

    // Handle product selection change
    const handleProductSelection = (ingredientName, productId) => {
      const selectedProduct = productOptions[ingredientName]?.find(p => p.product_id === productId);
      if (!selectedProduct) return;

      // Update selected products
      const newSelections = { ...selectedProducts, [ingredientName]: productId };
      setSelectedProducts(newSelections);

      // Update cart items with new selection
      const updatedCartItems = cartItems.map(item => {
        if (item.ingredient_name === ingredientName) {
          return {
            ...item,
            name: selectedProduct.name,
            price: parseFloat(selectedProduct.price),
            product_id: selectedProduct.product_id
          };
        }
        return item;
      });

      setCartItems(updatedCartItems);

      // Regenerate affiliate URL
      // Generate Walmart URL with correct format: items=ID1,ID2_quantity,ID3
      const walmartItems = [];
      const finalQuantities = {};
      
      // Count quantities for each product
      updatedCartItems.forEach(item => {
        if (item.product_id) {
          const quantity = (typeof item.quantity === 'number' && item.quantity > 0) ? item.quantity : 1;
          const qty = finalQuantities[item.product_id] || 0;
          finalQuantities[item.product_id] = qty + quantity;
        }
      });
      
      // Format for Walmart URL: productId or productId_quantity
      Object.entries(finalQuantities).forEach(([productId, quantity]) => {
        if (productId) {
          if (quantity === 1) {
            walmartItems.push(productId);
          } else {
            walmartItems.push(`${productId}_${Math.floor(quantity)}`);
          }
        }
      });
      
      if (walmartItems.length > 0) {
        setFinalWalmartUrl(`https://affil.walmart.com/cart/addToCart?items=${walmartItems.join(',')}`);
      } else {
        setFinalWalmartUrl('');
      };

      console.log('✅ Product selection updated for', ingredientName, ':', selectedProduct.name);
    };

    // Update quantity and regenerate URL
    const updateQuantity = (index, newQuantity) => {
      if (newQuantity < 1) return;
      const updatedItems = cartItems.map((item, i) => 
        i === index ? { ...item, quantity: newQuantity } : item
      );
      setCartItems(updatedItems);
      
      // Generate Walmart URL with correct format: items=ID1,ID2_quantity,ID3
      const walmartItems = [];
      const finalQuantities = {};
      
      // Count quantities for each product
      updatedItems.forEach(item => {
        if (item.product_id) {
          const quantity = (typeof item.quantity === 'number' && item.quantity > 0) ? item.quantity : 1;
          const qty = finalQuantities[item.product_id] || 0;
          finalQuantities[item.product_id] = qty + quantity;
        }
      });
      
      // Format for Walmart URL: productId or productId_quantity
      Object.entries(finalQuantities).forEach(([productId, quantity]) => {
        if (productId) {
          if (quantity === 1) {
            walmartItems.push(productId);
          } else {
            walmartItems.push(`${productId}_${Math.floor(quantity)}`);
          }
        }
      });
      
      if (walmartItems.length > 0) {
        setFinalWalmartUrl(`https://affil.walmart.com/cart/addToCart?items=${walmartItems.join(',')}`);
      } else {
        setFinalWalmartUrl('');
      }
    };

    // Calculate total price
    const calculateTotal = () => {
      return cartItems.reduce((total, item) => total + (item.price * item.quantity), 0);
    };

    // Copy URL to clipboard
    const copyUrlToClipboard = async () => {
      try {
        await navigator.clipboard.writeText(finalWalmartUrl);
        showNotification('🎉 Walmart link copied! Open new tab and paste to shop. Your selections are saved - you can continue making changes.', 'success');
      } catch (err) {
        showNotification('❌ Failed to copy. Please copy manually from the text box above.', 'error');
      }
    };

    // Special layout for Starbucks recipes
    if (recipe?.drink_name || recipe?.base_drink || recipe?.ordering_script) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 p-4">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              {showBackButton && (
                <button
                  onClick={() => setCurrentScreen('dashboard')}
                  className="mb-4 flex items-center space-x-2 text-green-600 hover:text-green-700 font-medium"
                >
                  <span>←</span>
                  <span>Back to Dashboard</span>
                </button>
              )}
              
              <div className="text-center">
                <div className="text-6xl mb-4">☕</div>
                <h1 className="text-4xl font-bold text-gray-800 mb-2">{recipe.drink_name}</h1>
                <p className="text-lg text-gray-600">{recipe.description}</p>
              </div>
            </div>

            {/* Starbucks Recipe Card */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              
              {/* Base Drink Section */}
              <div className="mb-8">
                <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="mr-2">☕</span>
                  Base Drink
                </h3>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-lg font-medium text-gray-800">{recipe.base_drink}</p>
                </div>
              </div>

              {/* Modifications Section */}
              <div className="mb-8">
                <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="mr-2">🎨</span>
                  Modifications
                </h3>
                <div className="space-y-3">
                  {recipe.modifications?.map((modification, index) => (
                    <div key={index} className="flex items-start p-4 bg-gray-50 rounded-lg">
                      <span className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center font-bold text-sm mr-4 mt-0.5">
                        {index + 1}
                      </span>
                      <p className="text-gray-800 leading-relaxed">{modification}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Ordering Script Section */}
              <div className="mb-8">
                <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                  <span className="mr-2">💬</span>
                  How to Order
                </h3>
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-6 rounded-lg">
                  <p className="text-lg text-gray-800 italic">"{recipe.ordering_script}"</p>
                </div>
              </div>

              {/* Pro Tips Section */}
              {recipe.pro_tips && recipe.pro_tips.length > 0 && (
                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                    <span className="mr-2">💡</span>
                    Pro Tips
                  </h3>
                  <div className="space-y-3">
                    {recipe.pro_tips.map((tip, index) => (
                      <div key={index} className="flex items-start p-4 bg-blue-50 rounded-lg">
                        <span className="text-blue-500 mr-3 mt-1">•</span>
                        <p className="text-gray-800">{tip}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Why Amazing Section */}
              {recipe.why_amazing && (
                <div className="mb-8">
                  <h3 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
                    <span className="mr-2">🔥</span>
                    Why This Drink is Amazing
                  </h3>
                  <div className="bg-purple-50 rounded-lg p-6">
                    <p className="text-gray-800 leading-relaxed">{recipe.why_amazing}</p>
                  </div>
                </div>
              )}

              {/* Share Section */}
              <div className="text-center">
                <h3 className="text-xl font-bold text-gray-800 mb-4">Share this Starbucks hack!</h3>
                <p className="text-gray-600 mb-4">Spread the word about this amazing drink creation</p>
                <div className="flex justify-center space-x-4">
                  <button 
                    onClick={() => {
                      const text = `Try this amazing Starbucks hack: ${recipe.drink_name}! Order: ${recipe.ordering_script}`;
                      navigator.clipboard.writeText(text);
                      showNotification('📱 Recipe copied to clipboard!', 'success');
                    }}
                    className="bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 transition-colors"
                  >
                    📱 Copy Recipe
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (!recipe) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="text-center py-20">
              <div className="text-6xl mb-4">🍳</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">No Recipe Found</h2>
              <p className="text-gray-600">Please generate a recipe first to see the details.</p>
            </div>
          </div>
        </div>
      );
    }

    // NEW INGREDIENT SELECTION FOCUSED DESIGN
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 p-4">
        <div className="max-w-7xl mx-auto">
          
          {/* Header Section */}
          <div className="mb-8">
            {showBackButton && (
              <button
                onClick={() => setCurrentScreen('dashboard')}
                className="mb-6 flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-medium text-lg"
              >
                <span>←</span>
                <span>Back to Dashboard</span>
              </button>
            )}
            
            <div className="text-center bg-white rounded-2xl shadow-lg p-8 mb-8">
              <div className="text-6xl mb-4">🛒</div>
              <h1 className="text-4xl font-bold text-gray-800 mb-3">
                {recipe.title || 'Delicious Recipe'}
              </h1>
              <p className="text-lg text-gray-600 mb-6 max-w-2xl mx-auto">
                Choose your preferred products from Walmart for each ingredient
              </p>
              
              {/* Quick Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-2xl mx-auto">
                <div className="text-center p-3 bg-blue-50 rounded-xl">
                  <div className="text-2xl mb-1">🥘</div>
                  <div className="text-sm text-gray-600">Ingredients</div>
                  <div className="font-bold text-gray-800">{Object.keys(productOptions).length}</div>
                </div>
                <div className="text-center p-3 bg-green-50 rounded-xl">
                  <div className="text-2xl mb-1">🍽️</div>
                  <div className="text-sm text-gray-600">Servings</div>
                  <div className="font-bold text-gray-800">{recipe.servings || '4'}</div>
                </div>
                <div className="text-center p-3 bg-purple-50 rounded-xl">
                  <div className="text-2xl mb-1">⏱️</div>
                  <div className="text-sm text-gray-600">Prep Time</div>
                  <div className="font-bold text-gray-800">{recipe.prep_time || '30 min'}</div>
                </div>
                <div className="text-center p-3 bg-yellow-50 rounded-xl">
                  <div className="text-2xl mb-1">💰</div>
                  <div className="text-sm text-gray-600">Total Cost</div>
                  <div className="font-bold text-green-600">${calculateTotal().toFixed(2)}</div>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Left Column - Ingredient Selection */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-lg p-6">
                <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
                  <span className="mr-3">🎯</span>
                  Select Your Products
                  <span className="ml-auto text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                    Choose 1 of 3 options per ingredient
                  </span>
                </h2>
                
                {loadingCart ? (
                  <div className="text-center py-12">
                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-600 text-lg">Loading Walmart products...</p>
                    <p className="text-gray-500 text-sm mt-2">Finding the best deals for your ingredients</p>
                  </div>
                ) : (
                  <div className="space-y-8">
                    {Object.keys(productOptions).length === 0 ? (
                      <div className="text-center py-12">
                        <div className="text-6xl mb-4">🔍</div>
                        <h3 className="text-xl font-bold text-gray-800 mb-2">No Products Found</h3>
                        <p className="text-gray-600">We couldn't find Walmart products for this recipe's ingredients.</p>
                      </div>
                    ) : (
                      Object.entries(productOptions).map(([ingredientName, ingredientOptions], index) => {
                        const selectedProductId = selectedProducts[ingredientName];
                        
                        return (
                          <div key={index} className="border-2 border-gray-200 rounded-xl p-6 hover:border-blue-300 transition-colors">
                            {/* Ingredient Header */}
                            <div className="flex items-center mb-6">
                              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold text-lg mr-4">
                                {index + 1}
                              </div>
                              <div>
                                <h3 className="text-xl font-bold text-gray-800">{ingredientName}</h3>
                                <p className="text-gray-600 text-sm">Choose your preferred option below</p>
                              </div>
                            </div>
                            
                            {/* Product Options Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              {ingredientOptions.slice(0, 3).map((product, productIndex) => (
                                <div
                                  key={productIndex}
                                  className={`relative border-2 rounded-xl p-4 cursor-pointer transition-all duration-200 transform hover:scale-105 ${
                                    selectedProductId === product.product_id
                                      ? 'border-green-500 bg-green-50 shadow-lg'
                                      : 'border-gray-200 bg-white hover:border-blue-300 hover:shadow-md'
                                  }`}
                                  onClick={() => handleProductSelection(ingredientName, product.product_id)}
                                >
                                  {/* Selection Indicator */}
                                  <div className="absolute top-3 right-3">
                                    {selectedProductId === product.product_id ? (
                                      <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                                        <span className="text-white text-sm font-bold">✓</span>
                                      </div>
                                    ) : (
                                      <div className="w-6 h-6 border-2 border-gray-300 rounded-full hover:border-blue-500"></div>
                                    )}
                                  </div>
                                  
                                  {/* Product Image */}
                                  {product.image_url && (
                                    <div className="mb-3">
                                      <img 
                                        src={product.image_url} 
                                        alt={product.name}
                                        className="w-full h-32 object-cover rounded-lg"
                                        onError={(e) => { e.target.style.display = 'none'; }}
                                      />
                                    </div>
                                  )}
                                  
                                  {/* Product Name */}
                                  <h4 className="font-semibold text-gray-800 text-sm leading-tight mb-3 min-h-[40px]">
                                    {product.name}
                                  </h4>
                                  
                                  {/* Price */}
                                  <div className="text-center">
                                    <div className="text-2xl font-bold text-green-600 mb-1">
                                      ${parseFloat(product.price).toFixed(2)}
                                    </div>
                                    <div className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                      ID: {product.product_id}
                                    </div>
                                  </div>
                                  
                                  {/* Selection Button */}
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleProductSelection(ingredientName, product.product_id);
                                    }}
                                    className={`w-full mt-3 py-2 rounded-lg font-medium transition-colors ${
                                      selectedProductId === product.product_id
                                        ? 'bg-green-500 text-white'
                                        : 'bg-gray-100 text-gray-700 hover:bg-blue-100'
                                    }`}
                                  >
                                    {selectedProductId === product.product_id ? 'Selected' : 'Select'}
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Right Column - Shopping Cart & Checkout */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-4">
                
                {/* Cart Header */}
                <div className="text-center mb-6">
                  <div className="text-4xl mb-2">🛍️</div>
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">Your Cart</h3>
                  <p className="text-sm text-gray-600">Selected Walmart products</p>
                </div>

                {/* Selected Products List */}
                <div className="space-y-3 mb-6 max-h-64 overflow-y-auto">
                  {loadingCart ? (
                    <div className="text-center py-8">
                      <div className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
                      <p className="text-gray-600 text-sm">Loading cart...</p>
                    </div>
                  ) : cartItems.length > 0 ? (
                    cartItems.map((item, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-3">
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex-1">
                            <h4 className="font-medium text-gray-800 text-sm leading-tight">{item.name}</h4>
                            <p className="text-xs text-gray-500 mt-1">For: {item.ingredient_name}</p>
                          </div>
                        </div>
                        
                        <div className="flex justify-between items-center">
                          <div className="flex items-center space-x-2">
                            <button
                              onClick={() => updateQuantity(index, item.quantity - 1)}
                              disabled={item.quantity <= 1}
                              className="w-7 h-7 bg-red-500 text-white rounded-full hover:bg-red-600 disabled:opacity-50 flex items-center justify-center text-sm"
                            >
                              -
                            </button>
                            <span className="w-10 text-center font-bold text-sm">{item.quantity}</span>
                            <button
                              onClick={() => updateQuantity(index, item.quantity + 1)}
                              className="w-7 h-7 bg-green-500 text-white rounded-full hover:bg-green-600 flex items-center justify-center text-sm"
                            >
                              +
                            </button>
                          </div>
                          <div className="text-right">
                            <div className="font-bold text-green-600 text-lg">${(item.price * item.quantity).toFixed(2)}</div>
                            <div className="text-xs text-gray-500">${item.price.toFixed(2)} each</div>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <div className="text-3xl mb-2">🛒</div>
                      <p>No items selected</p>
                    </div>
                  )}
                </div>

                {/* Cart Summary */}
                <div className="border-t pt-4 mb-6">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm text-gray-600">Total Items:</span>
                    <span className="font-bold">{cartItems.reduce((total, item) => total + item.quantity, 0)}</span>
                  </div>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xl font-bold text-gray-800">Total:</span>
                    <span className="text-3xl font-bold text-green-600">${calculateTotal().toFixed(2)}</span>
                  </div>
                  <div className="text-xs text-gray-500 text-center">
                    <p>✅ Real Walmart prices & products</p>
                    <p>🔗 Affiliate link generated automatically</p>
                  </div>
                </div>

                {/* Walmart Checkout Section */}
                <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-xl p-4 mb-4">
                  <div className="text-center mb-3">
                    <div className="text-2xl mb-1">🏪</div>
                    <h4 className="font-bold text-yellow-800 text-lg">Walmart Checkout</h4>
                    <p className="text-xs text-yellow-700 mb-3">Your personalized shopping link</p>
                  </div>
                  
                  <div className="bg-white rounded-lg p-3 mb-3">
                    <textarea
                      value={finalWalmartUrl || 'Loading...'}
                      readOnly
                      className="w-full h-20 p-2 border border-yellow-300 rounded-lg bg-gray-50 text-xs resize-none font-mono"
                      onClick={(e) => e.target.select()}
                    />
                  </div>
                  
                  <button
                    onClick={copyUrlToClipboard}
                    disabled={!finalWalmartUrl || cartItems.length === 0}
                    className="w-full bg-yellow-500 text-white font-bold py-3 px-4 rounded-lg hover:bg-yellow-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    📋 Copy & Shop at Walmart
                  </button>
                </div>

                {/* Instructions */}
                <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                  <h4 className="font-bold text-blue-800 mb-2 text-sm">🎯 How to Shop:</h4>
                  <ol className="text-xs text-blue-700 space-y-1">
                    <li>1. Choose your preferred products above</li>
                    <li>2. Adjust quantities using +/- buttons</li>
                    <li>3. Click "Copy & Shop at Walmart"</li>
                    <li>4. Open new tab & paste the link</li>
                    <li>5. All items will be in your Walmart cart</li>
                  </ol>
                  <div className="mt-3 p-2 bg-blue-100 rounded-lg">
                    <p className="text-xs text-blue-600">
                      <strong>💡 Pro Tip:</strong> Your selections are saved! You can change products or quantities and generate a new link anytime.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Recipe History Screen Component with Categories
  const RecipeHistoryScreen = () => {
    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeCategory, setActiveCategory] = useState('all');
    const [stats, setStats] = useState({
      total_count: 0,
      regular_recipes: 0,
      starbucks_recipes: 0
    });

    const categories = [
      { id: 'all', label: 'All', icon: '📝', color: 'bg-gray-500' },
      { id: 'cuisine', label: 'Cuisine', icon: '🍝', color: 'bg-orange-500' },
      { id: 'snacks', label: 'Snacks', icon: '🍪', color: 'bg-purple-500' },
      { id: 'beverages', label: 'Beverages', icon: '🧋', color: 'bg-blue-500' },
      { id: 'starbucks', label: 'Starbucks', icon: '☕', color: 'bg-green-500' }
    ];

    useEffect(() => {
      fetchRecipes();
    }, []);

    const fetchRecipes = async () => {
      try {
        setLoading(true);
        const response = await axios.get(`${API}/api/recipes/history/${user?.id || 'demo_user'}`);
        
        if (response.data.success) {
          setRecipes(response.data.recipes);
          setStats({
            total_count: response.data.total_count,
            regular_recipes: response.data.regular_recipes,
            starbucks_recipes: response.data.starbucks_recipes
          });
        } else {
          setRecipes([]);
        }
      } catch (error) {
        console.error('Error fetching recipes:', error);
        showNotification('❌ Failed to load recipe history', 'error');
        setRecipes([]);
      } finally {
        setLoading(false);
      }
    };

    const filteredRecipes = activeCategory === 'all' 
      ? recipes 
      : recipes.filter(recipe => recipe.category === activeCategory);

    const getCategoryCount = (categoryId) => {
      if (categoryId === 'all') return recipes.length;
      return recipes.filter(recipe => recipe.category === categoryId).length;
    };

    const viewRecipe = (recipe) => {
      if (recipe.type === 'starbucks') {
        // For Starbucks recipes, show them in the existing Starbucks detail view
        window.currentRecipe = recipe;
        setCurrentScreen('recipe-detail');
      } else {
        // For regular recipes, show them in the regular recipe detail view  
        window.currentRecipe = recipe;
        setCurrentScreen('recipe-detail');
      }
    };

    const deleteRecipe = async (recipeId, recipeType) => {
      if (window.confirm('Are you sure you want to delete this recipe?')) {
        try {
          const endpoint = recipeType === 'starbucks' ? 'starbucks-recipes' : 'recipes';
          await axios.delete(`${API}/api/${endpoint}/${recipeId}`);
          showNotification('✅ Recipe deleted successfully', 'success');
          fetchRecipes(); // Refresh the list
        } catch (error) {
          console.error('Error deleting recipe:', error);
          showNotification('❌ Failed to delete recipe', 'error');
        }
      }
    };

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    if (loading) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
          <div className="max-w-6xl mx-auto">
            <div className="text-center py-20">
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-500 mx-auto mb-4"></div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Loading Your Recipe History</h2>
              <p className="text-gray-600">Fetching all your amazing creations...</p>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-4">
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
            <div className="text-6xl mb-4">📖</div>
            <h1 className="text-4xl font-bold text-gray-800 mb-2">Recipe History</h1>
            <p className="text-lg text-gray-600">
              All your culinary creations in one place
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl mb-2">📝</div>
              <div className="text-2xl font-bold text-gray-800">{stats.total_count}</div>
              <div className="text-sm text-gray-600">Total Recipes</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl mb-2">🍳</div>
              <div className="text-2xl font-bold text-orange-600">{stats.regular_recipes}</div>
              <div className="text-sm text-gray-600">Food Recipes</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl mb-2">☕</div>
              <div className="text-2xl font-bold text-green-600">{stats.starbucks_recipes}</div>
              <div className="text-sm text-gray-600">Starbucks Drinks</div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div className="text-3xl mb-2">🏆</div>
              <div className="text-2xl font-bold text-purple-600">{filteredRecipes.length}</div>
              <div className="text-sm text-gray-600">Showing Now</div>
            </div>
          </div>

          {/* Category Filters */}
          <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Filter by Category</h3>
            <div className="flex flex-wrap gap-3">
              {categories.map(category => (
                <button
                  key={category.id}
                  onClick={() => setActiveCategory(category.id)}
                  className={`flex items-center px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                    activeCategory === category.id 
                      ? `${category.color} text-white shadow-lg` 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <span className="mr-2">{category.icon}</span>
                  <span>{category.label}</span>
                  <span className="ml-2 text-sm opacity-80">({getCategoryCount(category.id)})</span>
                </button>
              ))}
            </div>
          </div>

          {/* Recipe Grid */}
          {filteredRecipes.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-8xl mb-4">🍽️</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                {activeCategory === 'all' ? 'No Recipes Yet' : `No ${categories.find(c => c.id === activeCategory)?.label} Recipes`}
              </h2>
              <p className="text-gray-600 mb-6">
                {activeCategory === 'all' 
                  ? "Start creating some delicious recipes and viral Starbucks drinks!" 
                  : `Try creating some ${categories.find(c => c.id === activeCategory)?.label.toLowerCase()} recipes!`}
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button
                  onClick={() => setCurrentScreen('recipe-generation')}
                  className="bg-orange-500 hover:bg-orange-600 text-white font-bold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  🍳 Generate Recipe
                </button>
                <button
                  onClick={() => setCurrentScreen('starbucks-generator')}
                  className="bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-xl transition-all duration-200"
                >
                  ☕ Create Starbucks Drink
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredRecipes.map((recipe) => (
                <div key={recipe.id} className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
                  
                  {/* Recipe Header */}
                  <div className={`p-4 ${
                    recipe.category === 'cuisine' ? 'bg-gradient-to-r from-orange-500 to-red-500' :
                    recipe.category === 'snacks' ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                    recipe.category === 'beverages' ? 'bg-gradient-to-r from-blue-500 to-cyan-500' :
                    recipe.category === 'starbucks' ? 'bg-gradient-to-r from-green-500 to-teal-500' :
                    'bg-gradient-to-r from-gray-500 to-gray-600'
                  } text-white`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-2xl">{recipe.category_icon}</span>
                      <span className="text-xs opacity-80">{recipe.category_label}</span>
                    </div>
                    <h3 className="text-lg font-bold line-clamp-2">
                      {recipe.type === 'starbucks' ? recipe.drink_name : recipe.title}
                    </h3>
                  </div>

                  {/* Recipe Content */}
                  <div className="p-4">
                    <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                      {recipe.description}
                    </p>
                    
                    {recipe.type === 'starbucks' ? (
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center text-gray-600">
                          <span className="mr-2">🎯</span>
                          <span>Base: {recipe.base_drink}</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <span className="mr-2">🎨</span>
                          <span>{recipe.modifications?.length || 0} modifications</span>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2 text-sm">
                        <div className="flex items-center text-gray-600">
                          <span className="mr-2">⏱️</span>
                          <span>{recipe.prep_time + recipe.cook_time} min total</span>
                        </div>
                        <div className="flex items-center text-gray-600">
                          <span className="mr-2">🍽️</span>
                          <span>{recipe.servings} servings</span>
                        </div>
                      </div>
                    )}
                    
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex justify-between items-center">
                        <span className="text-xs text-gray-500">
                          {formatDate(recipe.created_at)}
                        </span>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => viewRecipe(recipe)}
                            className="bg-blue-500 hover:bg-blue-600 text-white text-xs px-3 py-1 rounded-lg transition-colors"
                          >
                            View
                          </button>
                          <button
                            onClick={() => deleteRecipe(recipe.id, recipe.type)}
                            className="bg-red-500 hover:bg-red-600 text-white text-xs px-3 py-1 rounded-lg transition-colors"
                          >
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  // For now, let me add a placeholder for other screens
  const OtherScreen = ({ screenName }) => (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">{screenName}</h1>
        <p className="text-gray-600 mb-4">This screen is being updated...</p>
        <button
          onClick={() => setCurrentScreen('dashboard')}
          className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
        >
          Back to Dashboard
        </button>
      </div>
    </div>
  );

  // Handle automatic screen navigation with useEffect to prevent render loops
  useEffect(() => {
    // If user is logged in and on landing, redirect to dashboard
    if (user && currentScreen === 'landing') {
      setCurrentScreen('dashboard');
    }
    
    // If user is not logged in and on protected screen, redirect to landing
    const protectedScreens = ['dashboard', 'generate-recipe', 'all-recipes', 'recipe-detail', 'starbucks-generator', 'welcome-onboarding', 'tutorial'];
    if (!user && protectedScreens.includes(currentScreen)) {
      const savedUser = localStorage.getItem('ai_chef_user');
      if (!savedUser) {
        console.log('🔄 No saved session found, redirecting to landing from:', currentScreen);
        setCurrentScreen('landing');
      }
    }
  }, [user, currentScreen]);

  // Main render function
  const renderScreen = () => {
    // Show loading screen while checking authentication
    if (isLoadingAuth) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">👨‍🍳</div>
            <div className="w-8 h-8 border-3 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
            <p className="text-gray-600">Loading AI Chef...</p>
          </div>
        </div>
      );
    }
    
    // Show loading if waiting for session restoration
    const protectedScreens = ['dashboard', 'generate-recipe', 'all-recipes', 'recipe-detail', 'starbucks-generator', 'welcome-onboarding', 'tutorial'];
    if (!user && protectedScreens.includes(currentScreen)) {
      const savedUser = localStorage.getItem('ai_chef_user');
      if (savedUser) {
        console.log('⏳ User session exists in localStorage, waiting for restoration...');
        return (
          <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">👨‍🍳</div>
              <div className="w-8 h-8 border-3 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
              <p className="text-gray-600">Restoring your session...</p>
            </div>
          </div>
        );
      }
    }
    
    switch (currentScreen) {
      case 'landing':
        return <LandingScreen />;
      case 'register':
        return <RegisterScreen />;
      case 'verify-email':
        return <EmailVerificationScreen />;
      case 'login':
        return <LoginScreen />;
      case 'forgot-password':
        return <ForgotPasswordScreen />;
      case 'reset-password':
        return <ResetPasswordScreen />;
      case 'dashboard':
        return <DashboardScreen />;
      case 'generate-recipe':
        return <RecipeGenerationScreen />;
      case 'all-recipes':
        return <RecipeHistoryScreen />;
      case 'recipe-detail':
        console.log('🚀 =================================');
        console.log('🚀 RENDERING RECIPE DETAIL SCREEN');
        console.log('🚀 =================================');
        console.log('🔍 Current screen state:', currentScreen);
        console.log('🔍 window.currentRecipe:', window.currentRecipe);
        console.log('🔍 Passing recipe prop:', window.currentRecipe);
        console.log('🔍 Render timestamp:', new Date().toISOString());
        return <RecipeDetailScreen recipe={window.currentRecipe} showBackButton={true} />;
      case 'starbucks-generator':
        return <StarbucksGeneratorScreen 
          showNotification={showNotification}
          setCurrentScreen={setCurrentScreen}
          user={user}
          API={API}
        />;
      case 'welcome-onboarding':
        return <WelcomeOnboarding 
          user={user}
          setCurrentScreen={setCurrentScreen}
          showNotification={showNotification}
        />;
      case 'tutorial':
        return <TutorialScreen 
          setCurrentScreen={setCurrentScreen}
          showNotification={showNotification}
        />;
      default:
        return <LandingScreen />;
    }
  };

  return (
    <div className="relative">
      {renderScreen()}
      
      {/* Global Notification */}
      {notification && (
        <div className={`fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 rounded-2xl shadow-lg text-white font-medium max-w-sm text-center ${
          notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
        }`}>
          {notification.message}
        </div>
      )}
    </div>
  );
}

export default App;