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
      case 'dashboard':
        return <DashboardScreen />;
      case 'generate-recipe':
        return <OtherScreen screenName="Recipe Generation" />;
      case 'all-recipes':
        return <OtherScreen screenName="Recipe History" />;
      case 'recipe-detail':
        return <OtherScreen screenName="Recipe Detail" />;
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