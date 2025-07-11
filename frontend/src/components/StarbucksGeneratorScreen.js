import React, { useState } from 'react';
import axios from 'axios';

// Starbucks Secret Menu Generator Screen
const StarbucksGeneratorScreen = () => {
  const [drinkType, setDrinkType] = useState('');
  const [flavorInspiration, setFlavorInspiration] = useState('');
  const [generatedDrink, setGeneratedDrink] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showCopySuccess, setShowCopySuccess] = useState(false);

  const drinkTypes = [
    { value: 'frappuccino', label: 'Frappuccino', emoji: '🥤' },
    { value: 'refresher', label: 'Refresher', emoji: '🧊' },
    { value: 'lemonade', label: 'Lemonade', emoji: '🍋' },
    { value: 'iced_matcha_latte', label: 'Iced Matcha Latte', emoji: '🍵' },
    { value: 'random', label: 'Surprise Me!', emoji: '🎲' }
  ];

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

  const copyOrderScript = () => {
    if (generatedDrink?.ordering_script) {
      navigator.clipboard.writeText(generatedDrink.ordering_script);
      setShowCopySuccess(true);
      setTimeout(() => setShowCopySuccess(false), 2000);
      showNotification('📋 Order script copied to clipboard!', 'success');
    }
  };

  const shareDrink = () => {
    const shareText = `Check out this amazing Starbucks secret menu drink: ${generatedDrink.drink_name}! 🤩\n\nOrder it like this: "${generatedDrink.ordering_script}"\n\n#StarbucksSecretMenu #DrinkHack`;
    
    if (navigator.share) {
      navigator.share({
        title: `${generatedDrink.drink_name} - Starbucks Secret Menu`,
        text: shareText,
        url: window.location.href
      });
    } else {
      navigator.clipboard.writeText(shareText);
      showNotification('📱 Drink details copied for sharing!', 'success');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-green-100 to-green-200 p-4">
      <div className="max-w-4xl mx-auto">
        
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">☕</div>
          <h1 className="text-4xl font-bold text-green-800 mb-2">Starbucks Secret Menu</h1>
          <p className="text-lg text-green-700">Generate viral TikTok-worthy drink hacks</p>
        </div>

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
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            
            {/* Drink Header */}
            <div className="bg-gradient-to-r from-green-600 to-green-700 text-white p-6">
              <div className="text-center">
                <div className="text-4xl mb-2">🎉</div>
                <h2 className="text-3xl font-bold mb-2">{generatedDrink.drink_name}</h2>
                <p className="text-green-100 text-lg">{generatedDrink.description}</p>
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
                  "{generatedDrink.ordering_script}"
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={copyOrderScript}
                    className={`flex-1 py-2 px-4 rounded-lg font-bold transition-all duration-200 ${
                      showCopySuccess 
                        ? 'bg-green-500 text-white' 
                        : 'bg-green-400 hover:bg-green-500 text-black'
                    }`}
                  >
                    {showCopySuccess ? '✅ Copied!' : '📋 Copy Order Script'}
                  </button>
                  
                  <button
                    onClick={shareDrink}
                    className="flex-1 py-2 px-4 rounded-lg bg-purple-500 hover:bg-purple-600 text-white font-bold transition-all duration-200"
                  >
                    📱 Share on TikTok
                  </button>
                </div>
              </div>
            </div>

            {/* Drink Details */}
            <div className="p-6 space-y-6">
              
              {/* Base Drink */}
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">☕</span>
                  Start With
                </h3>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-lg font-medium text-gray-800">{generatedDrink.base_drink}</p>
                </div>
              </div>

              {/* Modifications */}
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
                  <span className="mr-2">🎨</span>
                  Add These Modifications
                </h3>
                <div className="space-y-2">
                  {generatedDrink.modifications?.map((mod, index) => (
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
              {generatedDrink.ingredients_breakdown && generatedDrink.ingredients_breakdown.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
                    <span className="mr-2">📝</span>
                    What's Inside
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {generatedDrink.ingredients_breakdown.map((ingredient, index) => (
                      <span key={index} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">
                        {ingredient}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Pro Tips */}
              {generatedDrink.pro_tips && generatedDrink.pro_tips.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold text-gray-800 mb-3 flex items-center">
                    <span className="mr-2">💡</span>
                    Pro Tips
                  </h3>
                  <div className="space-y-2">
                    {generatedDrink.pro_tips.map((tip, index) => (
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
                  <p className="text-gray-800 leading-relaxed">{generatedDrink.why_amazing}</p>
                </div>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="p-6 bg-gray-50 border-t">
              <div className="flex space-x-4">
                <button
                  onClick={() => {
                    setGeneratedDrink(null);
                    setDrinkType('');
                    setFlavorInspiration('');
                  }}
                  className="flex-1 py-3 px-6 rounded-xl bg-gray-500 hover:bg-gray-600 text-white font-bold transition-colors"
                >
                  🔄 Generate Another
                </button>
                
                <button
                  onClick={() => setCurrentScreen('dashboard')}
                  className="flex-1 py-3 px-6 rounded-xl bg-green-500 hover:bg-green-600 text-white font-bold transition-colors"
                >
                  ← Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StarbucksGeneratorScreen;