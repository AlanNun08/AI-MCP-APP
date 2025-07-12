import React, { useState, useEffect } from 'react';
import axios from 'axios';

// Starbucks Secret Menu Generator Screen with Community Features
const StarbucksGeneratorScreen = ({ showNotification, setCurrentScreen, user, API }) => {
  const [drinkType, setDrinkType] = useState('');
  const [flavorInspiration, setFlavorInspiration] = useState('');
  const [generatedDrink, setGeneratedDrink] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showCopySuccess, setShowCopySuccess] = useState(false);
  
  // New state for community features
  const [currentTab, setCurrentTab] = useState('generator'); // generator, curated, community
  const [curatedRecipes, setCuratedRecipes] = useState([]);
  const [communityRecipes, setCommunityRecipes] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLoadingRecipes, setIsLoadingRecipes] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareFormData, setShareFormData] = useState({
    recipe_name: '',
    description: '',
    ingredients: ['', '', ''],
    order_instructions: '',
    category: 'frappuccino',
    tags: [],
    difficulty_level: 'easy',
    image_base64: null
  });
  const [isSharing, setIsSharing] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);

  const drinkTypes = [
    { value: 'frappuccino', label: 'Frappuccino', emoji: '🥤' },
    { value: 'refresher', label: 'Refresher', emoji: '🧊' },
    { value: 'lemonade', label: 'Lemonade', emoji: '🍋' },
    { value: 'iced_matcha_latte', label: 'Iced Matcha Latte', emoji: '🍵' },
    { value: 'random', label: 'Surprise Me!', emoji: '🎲' }
  ];

  const categories = [
    { value: 'all', label: 'All Recipes', emoji: '🌟' },
    { value: 'frappuccino', label: 'Frappuccino', emoji: '🥤' },
    { value: 'refresher', label: 'Refresher', emoji: '🧊' },
    { value: 'lemonade', label: 'Lemonade', emoji: '🍋' },
    { value: 'iced_matcha_latte', label: 'Iced Matcha', emoji: '🍵' },
    { value: 'random', label: 'Other', emoji: '🎲' }
  ];

  // Load curated and community recipes
  useEffect(() => {
    if (currentTab === 'curated' || currentTab === 'community') {
      loadRecipes();
    }
  }, [currentTab, selectedCategory]);

  const loadRecipes = async () => {
    setIsLoadingRecipes(true);
    try {
      if (currentTab === 'curated') {
        const response = await axios.get(`${API}/api/curated-starbucks-recipes?category=${selectedCategory}`);
        setCuratedRecipes(response.data.recipes || []);
      } else if (currentTab === 'community') {
        const response = await axios.get(`${API}/api/shared-recipes?category=${selectedCategory}&limit=20`);
        setCommunityRecipes(response.data.recipes || []);
      }
    } catch (error) {
      console.error('Error loading recipes:', error);
      showNotification('Failed to load recipes', 'error');
    } finally {
      setIsLoadingRecipes(false);
    }
  };

  const generateDrink = async () => {
    if (!drinkType) {
      showNotification('Please select a drink type!', 'error');
      return;
    }

    setIsGenerating(true);
    
    try {
      const response = await axios.post(`${API}/api/generate-starbucks-drink`, {
        user_id: user?.id || 'demo_user',
        drink_type: drinkType,
        flavor_inspiration: flavorInspiration || null
      });

      setGeneratedDrink(response.data);
      showNotification('🎉 Your secret menu drink is ready!', 'success');
    } catch (error) {
      console.error('Error generating drink:', error);
      showNotification('Failed to generate drink. Please try again.', 'error');
    } finally {
      setIsGenerating(false);
    }
  };

  const copyOrderScript = (orderScript) => {
    if (orderScript) {
      navigator.clipboard.writeText(orderScript);
      setShowCopySuccess(true);
      setTimeout(() => setShowCopySuccess(false), 2000);
      showNotification('📋 Order script copied to clipboard!', 'success');
    }
  };

  const shareDrink = (drink) => {
    const drinkName = drink.drink_name || drink.name || drink.recipe_name;
    const orderScript = drink.ordering_script || drink.order_instructions;
    const shareText = `Check out this amazing Starbucks secret menu drink: ${drinkName}! 🤩\n\nOrder it like this: "${orderScript}"\n\n#StarbucksSecretMenu #DrinkHack`;
    
    if (navigator.share) {
      navigator.share({
        title: `${drinkName} - Starbucks Secret Menu`,
        text: shareText,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(shareText);
      showNotification('📱 Drink details copied for sharing!', 'success');
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        showNotification('Image size should be less than 5MB', 'error');
        return;
      }
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target.result;
        setShareFormData(prev => ({ ...prev, image_base64: base64 }));
        setImagePreview(base64);
      };
      reader.readAsDataURL(file);
    }
  };

  const shareRecipe = async () => {
    if (!user?.id) {
      showNotification('Please sign in to share recipes', 'error');
      return;
    }

    if (!shareFormData.recipe_name || !shareFormData.description) {
      showNotification('Please fill in recipe name and description', 'error');
      return;
    }

    const nonEmptyIngredients = shareFormData.ingredients.filter(ing => ing.trim());
    if (nonEmptyIngredients.length < 2) {
      showNotification('Please add at least 2 ingredients', 'error');
      return;
    }

    setIsSharing(true);
    try {
      await axios.post(`${API}/api/share-recipe?user_id=${user.id}`, {
        ...shareFormData,
        ingredients: nonEmptyIngredients,
        tags: shareFormData.tags.filter(tag => tag.trim())
      });

      showNotification('🎉 Recipe shared successfully!', 'success');
      setShowShareModal(false);
      setShareFormData({
        recipe_name: '',
        description: '',
        ingredients: ['', '', ''],
        order_instructions: '',
        category: 'frappuccino',
        tags: [],
        difficulty_level: 'easy',
        image_base64: null
      });
      setImagePreview(null);
      
      // Reload community recipes if on that tab
      if (currentTab === 'community') {
        loadRecipes();
      }
    } catch (error) {
      console.error('Error sharing recipe:', error);
      showNotification('Failed to share recipe. Please try again.', 'error');
    } finally {
      setIsSharing(false);
    }
  };

  const likeRecipe = async (recipeId) => {
    if (!user?.id) {
      showNotification('Please sign in to like recipes', 'error');
      return;
    }

    try {
      const response = await axios.post(`${API}/api/like-recipe`, {
        recipe_id: recipeId,
        user_id: user.id
      });

      // Update the recipe in the local state
      setCommunityRecipes(prev => prev.map(recipe => 
        recipe.id === recipeId 
          ? {
              ...recipe,
              likes_count: response.data.likes_count,
              liked_by_users: response.data.action === 'liked' 
                ? [...(recipe.liked_by_users || []), user.id]
                : (recipe.liked_by_users || []).filter(uid => uid !== user.id)
            }
          : recipe
      ));

      showNotification(`Recipe ${response.data.action}! ❤️`, 'success');
    } catch (error) {
      console.error('Error liking recipe:', error);
      showNotification('Failed to like recipe', 'error');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-green-100 to-green-200 p-4">
      <div className="max-w-6xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">☕</div>
          <h1 className="text-4xl font-bold text-green-800 mb-2">Starbucks Secret Menu</h1>
          <p className="text-lg text-green-700">Generate, discover, and share viral drink hacks</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-2xl shadow-lg p-2 flex space-x-2">
            <button
              onClick={() => setCurrentTab('generator')}
              className={`px-6 py-3 rounded-xl font-bold transition-all duration-200 ${
                currentTab === 'generator'
                  ? 'bg-green-500 text-white shadow-md'
                  : 'text-gray-600 hover:text-green-600'
              }`}
            >
              ✨ AI Generator
            </button>
            <button
              onClick={() => setCurrentTab('curated')}
              className={`px-6 py-3 rounded-xl font-bold transition-all duration-200 ${
                currentTab === 'curated'
                  ? 'bg-purple-500 text-white shadow-md'
                  : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              📚 Curated Recipes
            </button>
            <button
              onClick={() => setCurrentTab('community')}
              className={`px-6 py-3 rounded-xl font-bold transition-all duration-200 ${
                currentTab === 'community'
                  ? 'bg-blue-500 text-white shadow-md'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              👥 Community
            </button>
          </div>
        </div>

        {/* AI Generator Tab */}
        {currentTab === 'generator' && (
          <>
            {/* Generator Form */}
            <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Create Your Secret Drink</h2>
              
              {/* Drink Type Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-3">Choose Your Drink Type</label>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  {drinkTypes.map((type) => (
                    <button
                      key={type.value}
                      onClick={() => setDrinkType(type.value)}
                      className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                        drinkType === type.value 
                          ? 'border-green-500 bg-green-50 text-green-700' 
                          : 'border-gray-200 hover:border-green-300 text-gray-700'
                      }`}
                    >
                      <div className="text-2xl mb-1">{type.emoji}</div>
                      <div className="font-medium text-sm">{type.label}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Flavor Inspiration */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Flavor Inspiration (Optional)</label>
                <input
                  type="text"
                  value={flavorInspiration}
                  onChange={(e) => setFlavorInspiration(e.target.value)}
                  placeholder='e.g., "tres leches", "ube", "mango tajin", "birthday cake"'
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">Add a flavor twist to inspire your drink creation!</p>
              </div>

              {/* Generate Button */}
              <button
                onClick={generateDrink}
                disabled={isGenerating}
                className={`w-full py-4 rounded-xl font-bold text-lg transition-all duration-200 ${
                  isGenerating 
                    ? 'bg-gray-400 text-gray-600 cursor-not-allowed' 
                    : 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white shadow-lg hover:shadow-xl'
                }`}
              >
                {isGenerating ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                    Brewing Your Secret Drink...
                  </span>
                ) : (
                  <span>✨ Generate My Secret Drink ✨</span>
                )}
              </button>
            </div>

            {/* Generated Drink Display */}
            {generatedDrink && (
              <DrinkCard 
                drink={generatedDrink} 
                showFullDetails={true}
                onCopyOrder={() => copyOrderScript(generatedDrink.ordering_script)}
                onShare={() => shareDrink(generatedDrink)}
                onGenerateAnother={() => {
                  setGeneratedDrink(null);
                  setDrinkType('');
                  setFlavorInspiration('');
                }}
                onBackToDashboard={() => setCurrentScreen('dashboard')}
                showActionButtons={true}
              />
            )}
          </>
        )}

        {/* Curated & Community Recipes Tabs */}
        {(currentTab === 'curated' || currentTab === 'community') && (
          <>
            {/* Category Filter */}
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
              <div className="flex flex-wrap justify-between items-center gap-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-800">
                    {currentTab === 'curated' ? '📚 Curated Recipes' : '👥 Community Recipes'}
                  </h3>
                  <p className="text-gray-600">
                    {currentTab === 'curated' 
                      ? 'Hand-picked favorites from our team' 
                      : 'Amazing creations shared by our community'
                    }
                  </p>
                </div>
                
                {currentTab === 'community' && (
                  <button
                    onClick={() => setShowShareModal(true)}
                    className="bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white px-6 py-3 rounded-xl font-bold transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    📸 Share Your Recipe
                  </button>
                )}
              </div>
              
              {/* Category Pills */}
              <div className="flex flex-wrap gap-2 mt-4">
                {categories.map((category) => (
                  <button
                    key={category.value}
                    onClick={() => setSelectedCategory(category.value)}
                    className={`px-4 py-2 rounded-full font-medium transition-all duration-200 ${
                      selectedCategory === category.value
                        ? 'bg-blue-500 text-white shadow-md'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {category.emoji} {category.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Recipes Grid */}
            {isLoadingRecipes ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                <p className="text-gray-600">Loading delicious recipes...</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {(currentTab === 'curated' ? curatedRecipes : communityRecipes).map((recipe, index) => (
                  <RecipeCard
                    key={recipe.id || index}
                    recipe={recipe}
                    isCommunity={currentTab === 'community'}
                    onLike={currentTab === 'community' ? () => likeRecipe(recipe.id) : null}
                    isLiked={currentTab === 'community' && recipe.liked_by_users?.includes(user?.id)}
                    onCopyOrder={() => copyOrderScript(recipe.order_instructions || recipe.ordering_script)}
                    onShare={() => shareDrink(recipe)}
                    user={user}
                  />
                ))}
              </div>
            )}

            {(currentTab === 'curated' ? curatedRecipes : communityRecipes).length === 0 && !isLoadingRecipes && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-bold text-gray-800 mb-2">No recipes found</h3>
                <p className="text-gray-600">
                  {currentTab === 'curated' 
                    ? 'Try selecting a different category'
                    : 'Be the first to share a recipe in this category!'
                  }
                </p>
              </div>
            )}
          </>
        )}

        {/* Share Recipe Modal */}
        {showShareModal && (
          <ShareRecipeModal
            isOpen={showShareModal}
            onClose={() => setShowShareModal(false)}
            formData={shareFormData}
            setFormData={setShareFormData}
            onImageUpload={handleImageUpload}
            imagePreview={imagePreview}
            onShare={shareRecipe}
            isSharing={isSharing}
            categories={drinkTypes}
          />
        )}

        {/* Back Button */}
        <div className="text-center mt-8">
          <button
            onClick={() => setCurrentScreen('dashboard')}
            className="bg-gray-500 hover:bg-gray-600 text-white px-8 py-3 rounded-xl font-bold transition-all duration-200"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default StarbucksGeneratorScreen;
  <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
    {/* Drink Header */}
    <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6">
      <div className="text-center">
        <div className="text-4xl mb-2">🎉</div>
        <h2 className="text-3xl font-bold mb-2">{drink.drink_name}</h2>
        <p className="text-green-100 text-lg">{drink.description}</p>
      </div>
    </div>

    {/* Drive-Thru Order Section */}
    <div className="p-6 bg-gray-900 text-green-400 font-mono">
      <div className="bg-black rounded-lg p-4 border border-green-400">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-400 rounded-full mr-2 animate-pulse"></div>
            <span className="text-sm">DRIVE-THRU ORDER READY</span>
          </div>
          <div className="text-xs text-gray-400">#{Math.floor(Math.random() * 1000)}</div>
        </div>
        
        <div className="text-lg mb-4 leading-relaxed">
          "{drink.ordering_script}"
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={onCopyOrder}
            className="flex-1 py-2 px-4 rounded-lg bg-green-400 hover:bg-green-500 text-black font-bold transition-all duration-200"
          >
            📋 Copy Order Script
          </button>
          
          <button
            onClick={onShare}
            className="flex-1 py-2 px-4 rounded-lg bg-purple-500 hover:bg-purple-600 text-white font-bold transition-all duration-200"
          >
            📱 Share on TikTok
          </button>
        </div>
      </div>
    </div>

    {showFullDetails && (
      <div className="p-6 space-y-6">
        {/* Base Drink */}
        <div>
          <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
            <span className="mr-2">☕</span>
            Start With
          </h3>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-lg font-medium text-gray-800">{drink.base_drink}</p>
          </div>
        </div>

        {/* Modifications */}
        <div>
          <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
            <span className="mr-2">🎨</span>
            Add These Modifications
          </h3>
          <div className="space-y-2">
            {drink.modifications?.map((mod, index) => (
              <div key={index} className="flex items-center p-3 bg-gray-50 rounded-lg">
                <span className="w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center font-bold text-sm mr-3">
                  {index + 1}
                </span>
                <span className="text-gray-800">{mod}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Ingredients Breakdown */}
        {drink.ingredients_breakdown && drink.ingredients_breakdown.length > 0 && (
          <div>
            <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
              <span className="mr-2">📝</span>
              What's Inside
            </h3>
            <div className="flex flex-wrap gap-2">
              {drink.ingredients_breakdown.map((ingredient, index) => (
                <span key={index} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
                  {ingredient}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Pro Tips */}
        {drink.pro_tips && drink.pro_tips.length > 0 && (
          <div>
            <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
              <span className="mr-2">💡</span>
              Pro Tips
            </h3>
            <div className="space-y-2">
              {drink.pro_tips.map((tip, index) => (
                <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg">
                  <span className="text-blue-500 mr-2 mt-1">•</span>
                  <span className="text-gray-800">{tip}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Why Amazing */}
        <div>
          <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
            <span className="mr-2">🔥</span>
            Why This Drink Slaps
          </h3>
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4">
            <p className="text-gray-800 leading-relaxed">{drink.why_amazing}</p>
          </div>
        </div>
      </div>
    )}

    {showActionButtons && (
      <div className="p-6 bg-gray-50 border-t">
        <div className="flex space-x-4">
          <button
            onClick={onGenerateAnother}
            className="flex-1 py-3 px-6 rounded-xl bg-gray-500 hover:bg-gray-600 text-white font-bold transition-colors"
          >
            🔄 Generate Another
          </button>
          
          <button
            onClick={onBackToDashboard}
            className="flex-1 py-3 px-6 rounded-xl bg-green-500 hover:bg-green-600 text-white font-bold transition-colors"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    )}
  </div>
);

// Recipe Card Component for Curated and Community Recipes
const RecipeCard = ({ recipe, isCommunity, onLike, isLiked, onCopyOrder, onShare, user }) => (
  <div className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-200">
    {/* Recipe Image */}
    {recipe.image_base64 && (
      <div className="h-48 bg-gradient-to-br from-green-100 to-blue-100 relative overflow-hidden">
        <img 
          src={recipe.image_base64} 
          alt={recipe.name || recipe.recipe_name}
          className="w-full h-full object-cover"
        />
      </div>
    )}
    
    {/* Recipe Header */}
    <div className="p-6">
      <div className="flex justify-between items-start mb-3">
        <h3 className="text-xl font-bold text-gray-800 line-clamp-2">
          {recipe.name || recipe.recipe_name}
        </h3>
        
        {isCommunity && (
          <div className="flex items-center space-x-2">
            <button
              onClick={onLike}
              disabled={!user?.id}
              className={`flex items-center space-x-1 px-3 py-1 rounded-full transition-all duration-200 ${
                isLiked 
                  ? 'bg-red-100 text-red-600' 
                  : 'bg-gray-100 text-gray-600 hover:bg-red-50 hover:text-red-500'
              }`}
            >
              <span className={isLiked ? '❤️' : '🤍'}></span>
              <span className="text-sm font-medium">{recipe.likes_count || 0}</span>
            </button>
          </div>
        )}
      </div>
      
      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {recipe.description || recipe.vibe}
      </p>
      
      {isCommunity && recipe.shared_by_username && (
        <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
          <span>by {recipe.shared_by_username}</span>
          {recipe.created_at && (
            <span>{new Date(recipe.created_at).toLocaleDateString()}</span>
          )}
        </div>
      )}
      
      {/* Ingredients Preview */}
      <div className="mb-4">
        <h4 className="font-medium text-gray-800 mb-2">Ingredients:</h4>
        <div className="space-y-1">
          {(recipe.ingredients || []).slice(0, 3).map((ingredient, index) => (
            <div key={index} className="text-sm text-gray-600 flex items-center">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2"></span>
              {ingredient}
            </div>
          ))}
          {(recipe.ingredients || []).length > 3 && (
            <div className="text-sm text-gray-500 italic">
              +{(recipe.ingredients || []).length - 3} more ingredients
            </div>
          )}
        </div>
      </div>
      
      {/* Tags */}
      {recipe.tags && recipe.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-4">
          {recipe.tags.slice(0, 3).map((tag, index) => (
            <span key={index} className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full">
              {tag}
            </span>
          ))}
        </div>
      )}
      
      {/* Action Buttons */}
      <div className="flex space-x-2">
        <button
          onClick={onCopyOrder}
          className="flex-1 bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-lg font-medium transition-colors text-sm"
        >
          📋 Copy Order
        </button>
        <button
          onClick={onShare}
          className="flex-1 bg-purple-500 hover:bg-purple-600 text-white py-2 px-4 rounded-lg font-medium transition-colors text-sm"
        >
          📱 Share
        </button>
      </div>
    </div>
  </div>
);

// Share Recipe Modal Component
const ShareRecipeModal = ({ isOpen, onClose, formData, setFormData, onImageUpload, imagePreview, onShare, isSharing, categories }) => {
  if (!isOpen) return null;

  const addIngredient = () => {
    setFormData(prev => ({
      ...prev,
      ingredients: [...prev.ingredients, '']
    }));
  };

  const removeIngredient = (index) => {
    setFormData(prev => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index)
    }));
  };

  const updateIngredient = (index, value) => {
    setFormData(prev => ({
      ...prev,
      ingredients: prev.ingredients.map((ing, i) => i === index ? value : ing)
    }));
  };

  const addTag = (tag) => {
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag]
      }));
    }
  };

  const removeTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800">📸 Share Your Recipe</h2>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 transition-colors"
            >
              <span className="text-2xl">×</span>
            </button>
          </div>

          <div className="space-y-6">
            {/* Recipe Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Recipe Name *</label>
              <input
                type="text"
                value={formData.recipe_name}
                onChange={(e) => setFormData(prev => ({ ...prev, recipe_name: e.target.value }))}
                placeholder="My Amazing Starbucks Creation"
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe what makes this drink special..."
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Category */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>
                    {cat.emoji} {cat.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Ingredients */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Ingredients * (minimum 2)</label>
              <div className="space-y-2">
                {formData.ingredients.map((ingredient, index) => (
                  <div key={index} className="flex space-x-2">
                    <input
                      type="text"
                      value={ingredient}
                      onChange={(e) => updateIngredient(index, e.target.value)}
                      placeholder={`Ingredient ${index + 1}`}
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                    {formData.ingredients.length > 3 && (
                      <button
                        onClick={() => removeIngredient(index)}
                        className="px-3 py-2 text-red-500 hover:text-red-700 transition-colors"
                      >
                        ×
                      </button>
                    )}
                  </div>
                ))}
                <button
                  onClick={addIngredient}
                  className="text-purple-500 hover:text-purple-700 font-medium transition-colors"
                >
                  + Add Ingredient
                </button>
              </div>
            </div>

            {/* Order Instructions */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Order Instructions</label>
              <textarea
                value={formData.order_instructions}
                onChange={(e) => setFormData(prev => ({ ...prev, order_instructions: e.target.value }))}
                placeholder="Hi, can I get a grande..."
                rows={2}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Image Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Recipe Photo</label>
              <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center">
                {imagePreview ? (
                  <div className="space-y-4">
                    <img src={imagePreview} alt="Preview" className="w-32 h-32 object-cover rounded-lg mx-auto" />
                    <button
                      onClick={() => {
                        setFormData(prev => ({ ...prev, image_base64: null }));
                        setImagePreview(null);
                      }}
                      className="text-red-500 hover:text-red-700 font-medium"
                    >
                      Remove Image
                    </button>
                  </div>
                ) : (
                  <div>
                    <div className="text-4xl mb-2">📸</div>
                    <p className="text-gray-600 mb-4">Upload a photo of your drink</p>
                    <input
                      type="file"
                      accept="image/*"
                      onChange={onImageUpload}
                      className="hidden"
                      id="image-upload"
                    />
                    <label
                      htmlFor="image-upload"
                      className="bg-purple-500 hover:bg-purple-600 text-white px-6 py-2 rounded-lg font-medium cursor-pointer transition-colors"
                    >
                      Choose Image
                    </label>
                    <p className="text-xs text-gray-500 mt-2">Max 5MB, JPG/PNG</p>
                  </div>
                )}
              </div>
            </div>

            {/* Tags */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
              <div className="flex flex-wrap gap-2 mb-2">
                {formData.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm flex items-center"
                  >
                    {tag}
                    <button
                      onClick={() => removeTag(tag)}
                      className="ml-2 text-purple-500 hover:text-purple-700"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
              <div className="flex flex-wrap gap-2">
                {['sweet', 'refreshing', 'caffeinated', 'fruity', 'creamy', 'iced', 'hot', 'seasonal'].map(tag => (
                  <button
                    key={tag}
                    onClick={() => addTag(tag)}
                    disabled={formData.tags.includes(tag)}
                    className={`px-3 py-1 rounded-full text-sm transition-colors ${
                      formData.tags.includes(tag)
                        ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                        : 'bg-gray-100 text-gray-700 hover:bg-purple-100 hover:text-purple-700'
                    }`}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            {/* Difficulty */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty Level</label>
              <div className="flex space-x-4">
                {['easy', 'medium', 'hard'].map(level => (
                  <button
                    key={level}
                    onClick={() => setFormData(prev => ({ ...prev, difficulty_level: level }))}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      formData.difficulty_level === level
                        ? 'bg-purple-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {level.charAt(0).toUpperCase() + level.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex space-x-4 pt-6">
              <button
                onClick={onClose}
                className="flex-1 py-3 px-6 rounded-xl bg-gray-300 hover:bg-gray-400 text-gray-700 font-bold transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={onShare}
                disabled={isSharing}
                className={`flex-1 py-3 px-6 rounded-xl font-bold transition-colors ${
                  isSharing
                    ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                    : 'bg-purple-500 hover:bg-purple-600 text-white'
                }`}
              >
                {isSharing ? 'Sharing...' : '🚀 Share Recipe'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default StarbucksGeneratorScreen;