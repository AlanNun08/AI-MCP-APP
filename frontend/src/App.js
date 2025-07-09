import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // Use environment variable for backend URL
  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  const [currentScreen, setCurrentScreen] = useState('landing');
  const [user, setUser] = useState(null);
  const [users, setUsers] = useState([]);
  const [userRecipes, setUserRecipes] = useState([]);
  const [loadingRecipes, setLoadingRecipes] = useState(false);
  const [generatingRecipe, setGeneratingRecipe] = useState(false);
  const [notification, setNotification] = useState(null);
  const [pendingVerificationEmail, setPendingVerificationEmail] = useState(null);
  const [pendingResetEmail, setPendingResetEmail] = useState(null);

  // Notification system
  const showNotification = (message, type = 'success') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 4000);
  };

  // Landing Screen Component
  const LandingScreen = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-400 to-blue-500 flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4 animate-bounce">👨‍🍳</div>
        <h1 className="text-4xl font-bold text-white mb-2 drop-shadow-lg">AI Chef</h1>
        <p className="text-xl text-white mb-8 opacity-90 leading-relaxed">Personalized recipes with instant grocery delivery</p>
        <div className="space-y-4">
          <button
            onClick={() => setCurrentScreen('register')}
            className="w-full bg-white text-green-600 font-semibold py-4 px-8 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 hover:bg-gray-50 active:scale-95"
          >
            ✨ Get Started
          </button>
          <button
            onClick={() => setCurrentScreen('login')}
            className="w-full bg-transparent border-2 border-white text-white font-semibold py-4 px-8 rounded-2xl hover:bg-white hover:text-green-600 transition-all duration-200 active:scale-95"
          >
            🔑 I Have an Account
          </button>
        </div>
        <div className="mt-8 text-white/70 text-sm">
          <p>🤖 AI-powered • 🛒 Walmart delivery • 🍃 Healthy options</p>
        </div>
      </div>
    </div>
  );

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
      cuisine_type: '',
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

    const cuisineOptions = ['italian', 'mexican', 'chinese', 'indian', 'mediterranean', 'american', 'thai', 'japanese'];
    const dietaryOptions = ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo'];
    const difficultyOptions = ['easy', 'medium', 'hard'];

    const handleSubmit = async (e) => {
      e.preventDefault();
      
      if (!formData.cuisine_type) {
        showNotification('❌ Please select a cuisine type', 'error');
        return;
      }

      setIsGenerating(true);
      try {
        const requestData = {
          user_id: user.id,
          cuisine_type: formData.cuisine_type,
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

        const response = await axios.post(`${API}/api/recipes/generate`, requestData);
        
        // Store recipe and navigate to detail
        window.currentRecipe = response.data;
        setCurrentScreen('recipe-detail');
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
              {/* Cuisine Type */}
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

  // Recipe Detail Screen Component
  const RecipeDetailScreen = ({ recipe, showBackButton = false }) => {
    const [generatingCart, setGeneratingCart] = useState(false);
    const [walmartUrl, setWalmartUrl] = useState(null);
    const [cartProducts, setCartProducts] = useState([]);

    const generateGroceryCart = async () => {
      if (!recipe) return;
      
      setGeneratingCart(true);
      try {
        console.log('Generating cart for recipe:', recipe.id, 'user:', user.id);
        const response = await axios.post(`${API}/api/grocery/cart-options?recipe_id=${recipe.id}&user_id=${user.id}`);
        
        console.log('Cart response:', response.data);
        
        if (response.data && response.data.ingredient_options) {
          // Extract products with IDs from the response
          const products = response.data.ingredient_options
            .flatMap(ing => ing.options || [])
            .filter(opt => opt.product_id)
            .slice(0, 10); // Limit to first 10 products
          
          console.log('Extracted products:', products);
          
          const productIds = products.map(opt => opt.product_id);
          
          // Create Walmart URL with product IDs
          const generatedUrl = `https://www.walmart.com/cart?items=${productIds.join(',')}`;
          
          console.log('Generated URL:', generatedUrl);
          console.log('Products to display:', products);
          
          setWalmartUrl(generatedUrl);
          setCartProducts(products);
          showNotification('🛒 Walmart cart URL generated! Copy the link below.', 'success');
        } else {
          console.log('No ingredient_options in response:', response.data);
          showNotification('❌ No products found for this recipe.', 'error');
        }
      } catch (error) {
        console.error('Cart generation failed:', error);
        showNotification('❌ Failed to generate cart. Please try again.', 'error');
      } finally {
        setGeneratingCart(false);
      }
    };

    const copyUrlToClipboard = async () => {
      try {
        await navigator.clipboard.writeText(walmartUrl);
        showNotification('📋 URL copied to clipboard!', 'success');
      } catch (error) {
        showNotification('📋 Please manually copy the URL below.', 'info');
      }
    };

    if (!recipe) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-800 mb-4">No Recipe Found</h1>
            <button
              onClick={() => setCurrentScreen('dashboard')}
              className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-2xl mx-auto">
          {showBackButton && (
            <button
              onClick={() => setCurrentScreen('dashboard')}
              className="mb-4 text-gray-600 hover:text-gray-800 flex items-center space-x-2"
            >
              <span>←</span>
              <span>Back to Dashboard</span>
            </button>
          )}

          <div className="bg-white rounded-2xl shadow-sm p-6 mb-4">
            <div className="text-center mb-6">
              <h1 className="text-2xl font-bold text-gray-800 mb-2">{recipe.title}</h1>
              <p className="text-gray-600">{recipe.description}</p>
              
              <div className="flex justify-center space-x-4 mt-4 text-sm">
                <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full">
                  ⏱️ {recipe.prep_time}min prep
                </span>
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full">
                  🍽️ {recipe.servings} servings
                </span>
                {recipe.calories_per_serving && (
                  <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full">
                    🔥 {recipe.calories_per_serving} cal
                  </span>
                )}
              </div>
            </div>

            {/* Ingredients */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">🥘 Ingredients</h3>
              <ul className="space-y-2">
                {recipe.ingredients?.map((ingredient, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <span className="text-green-500 mt-1">•</span>
                    <span className="text-gray-700">{ingredient}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Instructions */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-3">👨‍🍳 Instructions</h3>
              <ol className="space-y-3">
                {recipe.instructions?.map((instruction, index) => (
                  <li key={index} className="flex items-start space-x-3">
                    <span className="bg-green-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium flex-shrink-0 mt-0.5">
                      {index + 1}
                    </span>
                    <span className="text-gray-700">{instruction}</span>
                  </li>
                ))}
              </ol>
            </div>

            {/* Grocery Cart Button */}
            <div className="border-t pt-6">
              <button
                onClick={generateGroceryCart}
                disabled={generatingCart}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-500 text-white font-semibold py-4 px-6 rounded-2xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
              >
                {generatingCart ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span>Generating Cart...</span>
                  </div>
                ) : (
                  '🛒 Generate Walmart Shopping Cart'
                )}
              </button>

              {/* Walmart URL Display */}
              {walmartUrl && (
                <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-xl">
                  <div className="flex items-center mb-3">
                    <span className="text-blue-600 font-semibold text-lg">🛒 Your Walmart Cart is Ready!</span>
                  </div>
                  
                  {cartProducts.length > 0 && (
                    <div className="mb-3">
                      <p className="text-sm text-gray-600 mb-2">Items found ({cartProducts.length}):</p>
                      <div className="text-xs text-gray-500 space-y-1">
                        {cartProducts.slice(0, 5).map((product, index) => (
                          <div key={index} className="flex justify-between">
                            <span className="truncate">{product.name || `Product ${product.product_id}`}</span>
                            <span className="text-green-600 font-medium">${product.price || 'Price TBD'}</span>
                          </div>
                        ))}
                        {cartProducts.length > 5 && (
                          <div className="text-gray-400 text-center">... and {cartProducts.length - 5} more items</div>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="mb-3">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Copy this URL and paste it in your browser:
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={walmartUrl}
                        readOnly
                        className="flex-1 p-3 border border-gray-300 rounded-lg bg-white text-sm font-mono"
                        onClick={(e) => e.target.select()}
                      />
                      <button
                        onClick={copyUrlToClipboard}
                        className="px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm font-medium"
                      >
                        📋 Copy
                      </button>
                    </div>
                  </div>

                  <div className="text-xs text-gray-500 space-y-1">
                    <p>🔗 This URL contains product IDs: {cartProducts.map(p => p.product_id).join(', ')}</p>
                    <p>💡 Tip: Open this URL in a new tab to add items to your Walmart cart</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Recipe History Screen Component  
  const RecipeHistoryScreen = () => {
    const [recipes, setRecipes] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      const fetchRecipes = async () => {
        try {
          const response = await axios.get(`${API}/api/users/${user.id}/recipes`);
          setRecipes(response.data);
        } catch (error) {
          console.error('Failed to fetch recipes:', error);
          showNotification('❌ Failed to load recipes', 'error');
        } finally {
          setLoading(false);
        }
      };

      if (user?.id) {
        fetchRecipes();
      }
    }, [user]);

    if (loading) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your recipes...</p>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center space-x-3 mb-6">
            <button
              onClick={() => setCurrentScreen('dashboard')}
              className="text-gray-600 hover:text-gray-800"
            >
              ← Back
            </button>
            <div>
              <h2 className="text-xl font-bold text-gray-800">📚 Recipe History</h2>
              <p className="text-gray-600 text-sm">{recipes.length} saved recipes</p>
            </div>
          </div>

          <div className="space-y-4">
            {recipes.length === 0 ? (
              <div className="bg-white rounded-2xl shadow-sm p-8 text-center">
                <div className="text-4xl mb-4">🍽️</div>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">No Recipes Yet</h3>
                <p className="text-gray-600 mb-4">Generate your first AI recipe to get started!</p>
                <button
                  onClick={() => setCurrentScreen('generate-recipe')}
                  className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600"
                >
                  Generate Recipe
                </button>
              </div>
            ) : (
              recipes.map((recipe) => (
                <div key={recipe.id} className="bg-white rounded-2xl shadow-sm p-4 hover:shadow-md transition-shadow cursor-pointer"
                     onClick={() => {
                       window.currentRecipe = recipe;
                       setCurrentScreen('recipe-detail');
                     }}>
                  <h3 className="font-semibold text-gray-800 mb-1">{recipe.title}</h3>
                  <p className="text-gray-600 text-sm mb-2">{recipe.description}</p>
                  <div className="flex space-x-2 text-xs">
                    <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {recipe.prep_time}min
                    </span>
                    <span className="bg-green-100 text-green-800 px-2 py-1 rounded">
                      {recipe.servings} servings
                    </span>
                    {recipe.calories_per_serving && (
                      <span className="bg-orange-100 text-orange-800 px-2 py-1 rounded">
                        {recipe.calories_per_serving} cal
                      </span>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
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

  // Main render function
  const renderScreen = () => {
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
        return <RecipeDetailScreen recipe={window.currentRecipe} showBackButton={true} />;
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