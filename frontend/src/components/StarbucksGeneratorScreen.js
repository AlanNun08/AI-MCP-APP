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