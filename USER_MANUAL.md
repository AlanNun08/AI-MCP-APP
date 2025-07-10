# 🍳 AI Chef - User Manual

## 🌟 Welcome to AI Chef!
**AI Chef** is your personal AI-powered recipe generator with instant Walmart grocery delivery integration. Generate personalized recipes and create interactive shopping carts with just a few clicks!

---

## 🚀 Getting Started

### 📱 **Accessing the App**
1. **Open your web browser** (Chrome, Firefox, Safari, Edge)
2. **Navigate to**: https://c988d9d7-9d97-4304-9bbb-57f48034c134.preview.emergentagent.com
3. **You'll see the beautiful AI Chef landing page** with gradient background and chef emoji

### 🎯 **Main Features**
- ✅ **AI Recipe Generation** - Create personalized recipes with OpenAI
- ✅ **Interactive Walmart Shopping Cart** - Add ingredients with quantity controls
- ✅ **Healthy & Budget Modes** - Customize recipes to your needs
- ✅ **Recipe History** - Save and access your favorite recipes
- ✅ **Email Verification** - Secure account management

---

## 👤 Account Setup

### 🔐 **Creating Your Account**
1. **Click "✨ Get Started"** on the landing page
2. **Fill out the registration form:**
   - **First Name & Last Name** (required)
   - **Email Address** (required)
   - **Password** (minimum 6 characters, required)
   - **Confirm Password** (required)
3. **Optional Preferences:**
   - **Dietary Preferences**: vegetarian, vegan, gluten-free, dairy-free, keto, paleo
   - **Allergies**: nuts, shellfish, eggs, dairy, soy, wheat
   - **Favorite Cuisines**: italian, mexican, chinese, indian, mediterranean, american
4. **Click "✨ Create Account"**

### 📧 **Email Verification**
1. **Check your email** for the verification code
2. **Enter the 6-digit code** on the verification screen
3. **Click "✅ Verify Email"**
4. **You'll be redirected to the dashboard**

**🔍 Debug Tip**: If you don't receive the email, you can get the verification code by visiting: `[APP_URL]/api/debug/verification-codes/YOUR_EMAIL`

### 🔑 **Logging In**
1. **Click "🔑 I Have an Account"** on the landing page
2. **Enter your email and password**
3. **Click "🔑 Sign In"**

### 🔒 **Password Reset**
1. **Click "🔒 Forgot your password?"** on the login page
2. **Enter your email address**
3. **Check your email** for the reset code
4. **Enter the 6-digit code** and your new password
5. **Click "🔑 Reset Password"**

---

## 🍽️ Recipe Generation

### 🎯 **Generating Your First Recipe**
1. **From the dashboard**, click "🎯 Generate AI Recipe"
2. **Fill out the recipe form:**

#### **Required Fields:**
- **Cuisine Type**: Select from italian, mexican, chinese, indian, mediterranean, american, thai, japanese

#### **Optional Fields:**
- **Dietary Preferences**: Check boxes for any dietary restrictions
- **Servings**: Number of people (1-12)
- **Difficulty**: Easy, Medium, or Hard
- **Ingredients on Hand**: Comma-separated list of ingredients you already have
- **Max Prep Time**: Maximum preparation time in minutes

#### **Special Modes:**
- **🍃 Healthy Mode**: 
  - Check the "Healthy Mode" checkbox
  - Set **Max Calories per Serving** (200-800)
- **💰 Budget Mode**:
  - Check the "Budget Mode" checkbox
  - Set **Max Budget** ($5-$100)

3. **Click "🤖 Generate Recipe"**
4. **Wait 2-5 seconds** for AI to create your personalized recipe

### 📖 **Recipe Details**
Your generated recipe will show:
- **Recipe Title & Description**
- **Preparation Time & Servings**
- **Calories per Serving** (if available)
- **Complete Ingredients List**
- **Step-by-Step Instructions**

---

## 🛒 Interactive Walmart Shopping Cart

### 🎯 **Creating Your Shopping Cart**
1. **On any recipe page**, scroll down to the "Ready to Shop?" section
2. **Click "🛒 Generate Walmart Shopping Cart"**
3. **Wait for the interactive cart to load** (you'll see a success message)

### 🛍️ **Using the Interactive Cart**
The interactive cart will display:

#### **Individual Item Cards:**
- **Product Name** (e.g., "Great Value Chicken Breast 2.5lb")
- **Price** (e.g., "$8.99")
- **Product ID** (for verification)

#### **Quantity Controls:**
- **Minus (-) Button**: Decrease quantity (minimum 1)
- **Plus (+) Button**: Increase quantity (no maximum limit)
- **Current Quantity**: Shows current number selected
- **Remove Button (🗑️)**: Remove item from cart entirely

#### **Real-Time Features:**
- **Total Price**: Updates automatically as you change quantities
- **Item Count**: Shows total items in cart
- **Reset Button**: Clear and start over

### ✅ **Confirming Your Cart**
1. **Adjust quantities** using the +/- buttons
2. **Remove unwanted items** using the 🗑️ button
3. **Click "✅ Confirm Cart & Generate Affiliate Link"**
4. **Your final Walmart affiliate URL will appear**

### 📋 **Using Your Affiliate Link**
1. **Click "📋 Copy Link"** to copy the URL to your clipboard
2. **Open a new browser tab**
3. **Paste the URL** in the address bar
4. **Press Enter** - all items will be automatically added to your Walmart cart
5. **Complete checkout** on Walmart's website

**💡 Pro Tip**: Make sure you're logged into your Walmart account for the best experience!

---

## 📚 Recipe History

### 📖 **Viewing Your Recipes**
1. **From the dashboard**, click "📚 Recipe History"
2. **View all your saved recipes** with:
   - Recipe titles and descriptions
   - Preparation time and servings
   - Calories per serving (if available)
3. **Click on any recipe** to view full details and generate a new shopping cart

### 🔄 **Regenerating Shopping Carts**
- **Any saved recipe** can be used to generate a new interactive shopping cart
- **Each cart generation** creates a fresh affiliate link
- **Quantities and items** can be customized each time

---

## 📱 Mobile Experience

### 📲 **Progressive Web App (PWA)**
- **Add to Home Screen**: Your browser may prompt to install as an app
- **Offline Capabilities**: Basic functionality works offline
- **Mobile Optimized**: All features work on phones and tablets

### 📱 **Mobile-Specific Features**
- **Touch-friendly buttons**: Easy to tap +/- quantity controls
- **Responsive design**: Adapts to any screen size
- **Fast loading**: Optimized for mobile networks

---

## 🎛️ Advanced Features

### 🍃 **Healthy Mode**
- **Calorie Control**: Set maximum calories per serving
- **Nutritional Focus**: AI prioritizes healthy ingredients
- **Dietary Restrictions**: Works with all dietary preferences

### 💰 **Budget Mode**
- **Cost Control**: Set maximum total ingredient cost
- **Smart Substitutions**: AI suggests cost-effective alternatives
- **Value Optimization**: Maximizes nutrition per dollar

### 🔄 **Recipe Customization**
- **Ingredient Substitutions**: Specify ingredients you have on hand
- **Serving Adjustments**: Scale recipes up or down
- **Difficulty Levels**: Choose complexity that matches your skill

---

## 🔧 Troubleshooting

### 🐛 **Common Issues**

#### **Email Not Received**
- **Check spam folder**
- **Wait 2-3 minutes** for email delivery
- **Use debug endpoint**: `[APP_URL]/api/debug/verification-codes/YOUR_EMAIL`

#### **Login Issues**
- **Verify email first** - unverified accounts can't log in
- **Check password** - minimum 6 characters required
- **Use password reset** if needed

#### **Recipe Generation Fails**
- **Check internet connection**
- **Try different cuisine types**
- **Reduce dietary restrictions** if too many selected

#### **Shopping Cart Not Loading**
- **Wait for full page load**
- **Check browser compatibility** (Chrome, Firefox, Safari, Edge)
- **Try hard refresh**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)

#### **Affiliate Link Not Working**
- **Copy the complete URL**
- **Paste in a new browser tab**
- **Ensure you're logged into Walmart**

### 🔄 **Cache Issues**
If you see old content:
1. **Hard refresh**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. **Clear browser cache**: F12 → Application → Storage → Clear site data
3. **Try incognito/private browsing**

---

## 🛡️ Privacy & Security

### 🔐 **Account Security**
- **Password Requirements**: Minimum 6 characters
- **Email Verification**: Required for account activation
- **Secure Authentication**: Industry-standard password hashing

### 📧 **Email Privacy**
- **Verification Only**: Emails only used for account verification and password reset
- **No Spam**: We don't send promotional emails
- **Data Protection**: Email addresses are securely stored

### 🛒 **Shopping Data**
- **No Purchase Tracking**: We don't track your Walmart purchases
- **Affiliate Links**: Generate anonymous URLs for Walmart
- **Recipe Privacy**: Your recipes are private to your account

---

## 🆘 Support

### 💬 **Getting Help**
- **User Manual**: This comprehensive guide
- **Debug Tools**: Available for troubleshooting
- **Browser Compatibility**: Works on all modern browsers

### 🐛 **Reporting Issues**
If you encounter problems:
1. **Note the exact error message**
2. **Check browser console** (F12 → Console)
3. **Try the troubleshooting steps** above
4. **Document the steps** to reproduce the issue

---

## 🚀 Quick Start Checklist

✅ **Account Setup**
- [ ] Register with email and password
- [ ] Verify email address
- [ ] Log in successfully

✅ **Recipe Generation**
- [ ] Select cuisine type
- [ ] Configure preferences (optional)
- [ ] Generate first recipe
- [ ] View recipe details

✅ **Shopping Cart**
- [ ] Click "Generate Walmart Shopping Cart"
- [ ] Adjust quantities with +/- buttons
- [ ] Confirm cart and generate affiliate link
- [ ] Copy link and test on Walmart

✅ **Recipe Management**
- [ ] View recipe history
- [ ] Generate new shopping carts from saved recipes
- [ ] Customize quantities for different occasions

---

## 🎉 Enjoy Your AI Chef Experience!

**AI Chef** makes cooking and grocery shopping effortless. Generate unlimited personalized recipes, create custom shopping carts, and enjoy seamless Walmart integration. Happy cooking! 👨‍🍳✨