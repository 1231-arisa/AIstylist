"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import { useSession, signIn, signOut } from "next-auth/react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Home, MessageSquare, ShoppingBag, Camera, ChevronRight, ChevronLeft, Sun, Search, Upload, Send, Cloud, CloudRain, CloudSnow, CloudDrizzle } from "lucide-react"
import { getWeatherData, getWeatherRecommendation } from "@/lib/weather"
import { useAuth } from "@/components/auth-provider"

export default function AIstylistApp() {
  const { data: session, status } = useSession()
  const { user, subscription, loading } = useAuth()
  const [activeOutfit, setActiveOutfit] = useState(0)
  const [activeCategory, setActiveCategory] = useState("All")
  const [weather, setWeather] = useState<any>(null)
  const [outfits, setOutfits] = useState<any[]>([])
  const [chatMessages, setChatMessages] = useState<any[]>([])
  const [chatInput, setChatInput] = useState("")
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [isLoadingOutfits, setIsLoadingOutfits] = useState(false)

  // Load weather data on component mount
  useEffect(() => {
    const loadWeather = async () => {
      try {
        const weatherData = await getWeatherData()
        setWeather(weatherData)
      } catch (error) {
        console.error('Failed to load weather:', error)
      }
    }
    loadWeather()
  }, [])

  // Load outfit recommendations
  useEffect(() => {
    if (user && subscription?.canUseFeatures) {
      loadOutfits()
    }
  }, [user, subscription])

  const loadOutfits = async () => {
    setIsLoadingOutfits(true)
    try {
      const response = await fetch(`/api/outfits?weather=${weather?.condition || 'moderate'}`)
      const data = await response.json()
      if (data.success) {
        setOutfits(data.outfits)
      }
    } catch (error) {
      console.error('Failed to load outfits:', error)
    } finally {
      setIsLoadingOutfits(false)
    }
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImage(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const sendChatMessage = async () => {
    if (!chatInput.trim() && !uploadedImage) return

    const newMessage = {
      id: Date.now(),
      message: chatInput,
      isUser: true,
      imageUrl: uploadedImage,
      timestamp: new Date()
    }
    setChatMessages(prev => [...prev, newMessage])
    setChatInput("")
    setUploadedImage(null)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: chatInput,
          imageBase64: uploadedImage,
          weather: weather?.condition,
          occasion: 'casual'
        })
      })
      const data = await response.json()
      
      if (data.success) {
        const aiMessage = {
          id: Date.now() + 1,
          message: data.reply,
          isUser: false,
          timestamp: new Date()
        }
        setChatMessages(prev => [...prev, aiMessage])
      }
    } catch (error) {
      console.error('Failed to send message:', error)
    }
  }

  const getWeatherIcon = (condition: string) => {
    const conditionLower = condition.toLowerCase()
    if (conditionLower.includes('sun') || conditionLower.includes('clear')) return <Sun className="w-4 h-4" />
    if (conditionLower.includes('cloud')) return <Cloud className="w-4 h-4" />
    if (conditionLower.includes('rain')) return <CloudRain className="w-4 h-4" />
    if (conditionLower.includes('snow')) return <CloudSnow className="w-4 h-4" />
    if (conditionLower.includes('drizzle')) return <CloudDrizzle className="w-4 h-4" />
    return <Sun className="w-4 h-4" />
  }

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-[#E8D0D0] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-[#9A9A9A]">Loading...</p>
        </div>
      </div>
    )
  }

  // Show login screen if not authenticated
  if (!session) {
    return (
      <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center">
        <Card className="p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <h1 className="text-2xl font-light mb-4">Welcome to AIstylist</h1>
            <p className="text-[#9A9A9A] mb-6">Your personal AI fashion assistant</p>
            <Button 
              onClick={() => signIn('google')}
              className="w-full bg-[#E8D0D0] hover:bg-[#E0C0C0] text-[#333333]"
            >
              Sign in with Google
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  // Show subscription required screen if trial expired
  if (subscription && !subscription.canUseFeatures) {
    return (
      <div className="min-h-screen bg-[#FAFAFA] flex items-center justify-center">
        <Card className="p-8 max-w-md w-full mx-4">
          <div className="text-center">
            <h1 className="text-2xl font-light mb-4">Trial Expired</h1>
            <p className="text-[#9A9A9A] mb-6">
              Your free trial has ended. Subscribe to continue using AIstylist.
            </p>
            <Button 
              onClick={() => window.location.href = '/api/stripe/checkout'}
              className="w-full bg-[#E8D0D0] hover:bg-[#E0C0C0] text-[#333333]"
            >
              Subscribe for $20/month
            </Button>
          </div>
        </Card>
      </div>
    )
  }

  const categories = ["All", "Tops", "Bottoms", "Dresses", "Outerwear", "Shoes", "Accessories"]

  const closetItems = [
    { id: 1, name: "White Blouse", category: "Tops", color: "bg-[#FAFAFA]" },
    { id: 2, name: "Beige Sweater", category: "Tops", color: "bg-[#F5F0E8]" },
    { id: 3, name: "Gray Pants", category: "Bottoms", color: "bg-[#E8E8E8]" },
    { id: 4, name: "Pink Dress", category: "Dresses", color: "bg-[#E8D0D0]" },
    { id: 5, name: "Cream Skirt", category: "Bottoms", color: "bg-[#F5F0E8]" },
    { id: 6, name: "Taupe Blazer", category: "Outerwear", color: "bg-[#E8E0D5]" },
    { id: 7, name: "Nude Heels", category: "Shoes", color: "bg-[#F0E5D8]" },
    { id: 8, name: "Pearl Necklace", category: "Accessories", color: "bg-[#FAFAFA]" },
    { id: 9, name: "Beige Cardigan", category: "Outerwear", color: "bg-[#F5F0E8]" },
    { id: 10, name: "Gray Tee", category: "Tops", color: "bg-[#E8E8E8]" },
    { id: 11, name: "Blush Blouse", category: "Tops", color: "bg-[#E8D0D0]" },
    { id: 12, name: "Ivory Sweater", category: "Tops", color: "bg-[#FAFAFA]" },
  ]

  const filteredItems =
    activeCategory === "All" ? closetItems : closetItems.filter((item) => item.category === activeCategory)

  const nextOutfit = () => {
    setActiveOutfit((prev) => (prev + 1) % outfits.length)
  }

  const prevOutfit = () => {
    setActiveOutfit((prev) => (prev - 1 + outfits.length) % outfits.length)
  }

  return (
    <div className="min-h-screen bg-[#FAFAFA] text-[#333333] font-sans">
      <Tabs defaultValue="home" className="w-full">
        {/* App Content */}
        <div className="pb-20">
          {/* Home Tab */}
          <TabsContent value="home" className="m-0">
            <div className="p-4 pt-12">
              {/* Header */}
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h1 className="text-2xl font-light tracking-wide">Good morning, {user?.name?.split(' ')[0] || 'there'}!</h1>
                  <p className="text-sm text-[#9A9A9A]">What would you like to wear today?</p>
                </div>
                <div className="flex items-center gap-3">
                  {weather && (
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-sm">
                        {getWeatherIcon(weather.condition)}
                        <span className="font-medium">{weather.temperature}°C</span>
                      </div>
                      <p className="text-xs text-[#9A9A9A]">{weather.condition}</p>
                    </div>
                  )}
                <div className="w-10 h-10 rounded-full bg-[#F5F0E8] flex items-center justify-center">
                    {user?.picture ? (
                      <Image src={user.picture} alt="Profile" width={40} height={40} className="rounded-full" />
                    ) : (
                      <span className="text-[#9A9A9A]">{user?.name?.[0] || 'U'}</span>
                    )}
                  </div>
                </div>
              </div>

              {/* Today's Outfit */}
              <div className="mb-8">
                <h2 className="text-lg font-light mb-4">Today's Outfit Recommendation</h2>
                {isLoadingOutfits ? (
                  <Card className="rounded-3xl border-0 shadow-sm p-8">
                    <div className="text-center">
                      <div className="w-8 h-8 border-4 border-[#E8D0D0] border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                      <p className="text-[#9A9A9A]">Generating outfit recommendations...</p>
                    </div>
                  </Card>
                ) : outfits.length > 0 ? (
                <Card className="rounded-3xl border-0 shadow-sm overflow-hidden">
                  <div className="relative">
                    {/* Outfit Navigation */}
                      {outfits.length > 1 && (
                        <>
                    <button
                      onClick={prevOutfit}
                      className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white/80 flex items-center justify-center z-10"
                    >
                      <ChevronLeft className="w-4 h-4 text-[#9A9A9A]" />
                    </button>
                    <button
                      onClick={nextOutfit}
                      className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-white/80 flex items-center justify-center z-10"
                    >
                      <ChevronRight className="w-4 h-4 text-[#9A9A9A]" />
                    </button>
                        </>
                      )}

                    {/* Outfit Image */}
                    <div className="bg-[#F5F0E8] h-[450px] flex items-center justify-center">
                      <Image
                          src={outfits[activeOutfit]?.imageUrl || "/images/female-avatar.png"}
                        alt="Outfit recommendation"
                        width={250}
                        height={400}
                        className="h-[400px] w-auto object-contain"
                      />
                    </div>

                    {/* Outfit Info */}
                    <div className="absolute bottom-0 left-0 right-0 bg-white/90 backdrop-blur-sm p-4">
                      <div className="flex justify-between items-center">
                        <div>
                            <h3 className="font-medium">{outfits[activeOutfit]?.name || 'Outfit Recommendation'}</h3>
                          <div className="flex items-center gap-2 mt-1">
                            <div className="flex items-center gap-1">
                                {getWeatherIcon(weather?.condition || 'sunny')}
                                <span className="text-xs text-[#9A9A9A]">{weather?.condition || 'Sunny'}, {weather?.temperature || 22}°C</span>
                              </div>
                              <span className="text-xs text-[#9A9A9A]">•</span>
                              <span className="text-xs text-[#9A9A9A]">{outfits[activeOutfit]?.occasion || 'Casual'}</span>
                            </div>
                            {outfits[activeOutfit]?.description && (
                              <p className="text-xs text-[#9A9A9A] mt-1">{outfits[activeOutfit].description}</p>
                            )}
                        </div>
                        <div className="flex gap-1">
                          {outfits.map((_, index) => (
                            <div
                              key={index}
                              className={`w-1.5 h-1.5 rounded-full ${activeOutfit === index ? "bg-[#E8D0D0]" : "bg-[#E8E8E8]"}`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </Card>
                ) : (
                  <Card className="rounded-3xl border-0 shadow-sm overflow-hidden">
                    <div className="relative">
                      {/* Default Avatar Image */}
                      <div className="bg-[#F5F0E8] h-[450px] flex items-center justify-center">
                        <Image
                          src="/images/female-avatar.png"
                          alt="Default avatar"
                          width={250}
                          height={400}
                          className="h-[400px] w-auto object-contain"
                        />
                      </div>

                      {/* Outfit Info */}
                      <div className="absolute bottom-0 left-0 right-0 bg-white/90 backdrop-blur-sm p-4">
                        <div className="flex justify-between items-center">
                          <div>
                            <h3 className="font-medium">No Outfit</h3>
                            <div className="flex items-center gap-2 mt-1">
                              <div className="flex items-center gap-1">
                                {getWeatherIcon(weather?.condition || 'sunny')}
                                <span className="text-xs text-[#9A9A9A]">{weather?.condition || 'Sunny'}</span>
                                <span className="text-xs text-[#9A9A9A]">•</span>
                                <span className="text-xs text-[#9A9A9A]">{weather?.temperature || '20'}°C</span>
                                <span className="text-xs text-[#9A9A9A]">•</span>
                                <span className="text-xs text-[#9A9A9A]">Casual</span>
                              </div>
                            </div>
                          </div>
                          <Button 
                            onClick={loadOutfits}
                            className="bg-[#E8D0D0] hover:bg-[#E0C0C0] text-[#333333] text-xs px-3 py-1"
                          >
                            Generate
                          </Button>
                        </div>
                      </div>
                    </div>
                  </Card>
                )}
              </div>

              {/* Quick Actions */}
              <div>
                <h2 className="text-lg font-light mb-4">Quick Actions</h2>
                <div className="grid grid-cols-2 gap-4">
                  <Card className="rounded-2xl border-0 shadow-sm p-4 bg-[#F5F0E8]">
                    <div className="flex flex-col items-center text-center">
                      <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center mb-2">
                        <Camera className="w-5 h-5 text-[#9A9A9A]" />
                      </div>
                      <h3 className="text-sm font-medium">Style an Outfit</h3>
                      <p className="text-xs text-[#9A9A9A] mt-1">Upload a photo to get feedback</p>
                    </div>
                  </Card>
                  <Card className="rounded-2xl border-0 shadow-sm p-4 bg-[#E8D0D0]">
                    <div className="flex flex-col items-center text-center">
                      <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center mb-2">
                        <MessageSquare className="w-5 h-5 text-[#9A9A9A]" />
                      </div>
                      <h3 className="text-sm font-medium">Ask AIstylist</h3>
                      <p className="text-xs text-[#9A9A9A] mt-1">Get fashion advice from AI</p>
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Chat Tab */}
          <TabsContent value="chat" className="m-0">
            <div className="p-4 pt-12">
              {/* Header */}
              <div className="mb-8">
                <h1 className="text-2xl font-light tracking-wide">Chat with AIstylist</h1>
                <p className="text-sm text-[#9A9A9A]">Get personalized fashion advice</p>
              </div>

              {/* Upload Area */}
              <Card className="rounded-3xl border-0 shadow-sm p-6 mb-6">
                <div className="border-2 border-dashed border-[#E8E8E8] rounded-2xl p-8 flex flex-col items-center justify-center">
                  <div className="w-12 h-12 rounded-full bg-[#F5F0E8] flex items-center justify-center mb-4">
                    <Camera className="w-6 h-6 text-[#9A9A9A]" />
                  </div>
                  <p className="text-sm font-medium mb-1">Upload an outfit photo</p>
                  <p className="text-xs text-[#9A9A9A] mb-4 text-center">Take a photo or upload from your gallery</p>
                  <input
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                    id="image-upload"
                  />
                  <label htmlFor="image-upload">
                    <Button asChild className="bg-[#E8D0D0] hover:bg-[#E0C0C0] text-[#333333] rounded-full">
                      <span>Choose Photo</span>
                    </Button>
                  </label>
                  {uploadedImage && (
                    <div className="mt-4">
                      <Image
                        src={uploadedImage}
                        alt="Uploaded outfit"
                        width={200}
                        height={200}
                        className="rounded-lg object-cover"
                      />
                    </div>
                  )}
                </div>
              </Card>

              {/* Conversation */}
              <Card className="rounded-3xl border-0 shadow-sm p-4 mb-6">
                <div className="space-y-4 max-h-[300px] overflow-y-auto mb-4">
                  {chatMessages.length === 0 ? (
                  <div className="bg-[#F5F0E8] rounded-2xl p-3 max-w-[80%]">
                    <p className="text-sm">Hello! How can I help with your style today?</p>
                      <p className="text-xs text-[#9A9A9A] mt-1">AIstylist • {new Date().toLocaleTimeString()}</p>
                  </div>
                  ) : (
                    chatMessages.map((message) => (
                      <div
                        key={message.id}
                        className={`rounded-2xl p-3 max-w-[80%] ${
                          message.isUser ? 'bg-[#E8E8E8] ml-auto' : 'bg-[#F5F0E8]'
                        }`}
                      >
                        {message.imageUrl && (
                          <div className="mb-2">
                            <Image
                              src={message.imageUrl}
                              alt="Uploaded outfit"
                              width={150}
                              height={150}
                              className="rounded-lg object-cover"
                            />
                  </div>
                        )}
                        <p className="text-sm">{message.message}</p>
                        <p className="text-xs text-[#9A9A9A] mt-1">
                          {message.isUser ? 'You' : 'AIstylist'} • {message.timestamp.toLocaleTimeString()}
                        </p>
                  </div>
                    ))
                  )}
                </div>

                <div className="flex gap-2">
                  <Input
                    placeholder="Ask anything about fashion..."
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                    className="rounded-full border-[#E8E8E8] focus-visible:ring-[#E8D0D0]"
                  />
                  <Button 
                    onClick={sendChatMessage}
                    className="rounded-full bg-[#E8D0D0] hover:bg-[#E0C0C0] text-[#333333] px-4"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
              </Card>

              {/* Suggested Questions */}
              <div>
                <h3 className="text-sm font-medium mb-3">Suggested Questions</h3>
                <div className="flex flex-wrap gap-2">
                  <Badge 
                    className="bg-[#F5F0E8] text-[#333333] hover:bg-[#E8E0D5] rounded-full cursor-pointer"
                    onClick={() => setChatInput("What colors match with gray?")}
                  >
                    What colors match with gray?
                  </Badge>
                  <Badge 
                    className="bg-[#F5F0E8] text-[#333333] hover:bg-[#E8E0D5] rounded-full cursor-pointer"
                    onClick={() => setChatInput("How to style a white blouse?")}
                  >
                    How to style a white blouse?
                  </Badge>
                  <Badge 
                    className="bg-[#F5F0E8] text-[#333333] hover:bg-[#E8E0D5] rounded-full cursor-pointer"
                    onClick={() => setChatInput("Casual outfit ideas")}
                  >
                    Casual outfit ideas
                  </Badge>
                </div>
              </div>
            </div>
          </TabsContent>

          {/* Closet Tab */}
          <TabsContent value="closet" className="m-0">
            <div className="p-4 pt-12">
              {/* Header */}
              <div className="mb-6">
                <h1 className="text-2xl font-light tracking-wide">My Closet</h1>
                <p className="text-sm text-[#9A9A9A]">All your saved items</p>
              </div>

              {/* Search */}
              <div className="relative mb-6">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#9A9A9A]" />
                <Input
                  placeholder="Search your closet..."
                  className="pl-10 rounded-full border-[#E8E8E8] focus-visible:ring-[#E8D0D0]"
                />
              </div>

              {/* Categories */}
              <div className="mb-6 overflow-x-auto">
                <div className="flex gap-2 min-w-max">
                  {categories.map((category) => (
                    <Button
                      key={category}
                      variant="outline"
                      className={`rounded-full px-4 py-1 h-auto text-sm ${
                        activeCategory === category
                          ? "bg-[#E8D0D0] text-[#333333] border-[#E8D0D0]"
                          : "bg-transparent text-[#9A9A9A] border-[#E8E8E8]"
                      }`}
                      onClick={() => setActiveCategory(category)}
                    >
                      {category}
                    </Button>
                  ))}
                </div>
              </div>

              {/* Closet Grid */}
              <div className="grid grid-cols-3 gap-4">
                {filteredItems.map((item) => (
                  <Card key={item.id} className="rounded-2xl border-0 shadow-sm overflow-hidden">
                    <div className={`h-32 ${item.color} flex items-center justify-center`}>
                      <ShoppingBag className="w-8 h-8 text-[#9A9A9A]" />
                    </div>
                    <div className="p-2">
                      <p className="text-xs font-medium truncate">{item.name}</p>
                      <p className="text-xs text-[#9A9A9A]">{item.category}</p>
                    </div>
                  </Card>
                ))}
              </div>

              {/* Add Item Button */}
              <Button className="fixed bottom-24 right-4 w-12 h-12 rounded-full bg-[#E8D0D0] hover:bg-[#E0C0C0] text-[#333333] p-0">
                +
              </Button>
            </div>
          </TabsContent>
        </div>

        {/* Bottom Navigation */}
        <TabsList className="fixed bottom-0 left-0 right-0 h-16 grid grid-cols-3 bg-white border-t border-[#E8E8E8] rounded-none">
          <TabsTrigger
            value="home"
            className="data-[state=active]:bg-transparent data-[state=active]:text-[#E8D0D0] text-[#9A9A9A]"
          >
            <div className="flex flex-col items-center">
              <Home className="w-5 h-5" />
              <span className="text-xs mt-1">Home</span>
            </div>
          </TabsTrigger>
          <TabsTrigger
            value="chat"
            className="data-[state=active]:bg-transparent data-[state=active]:text-[#E8D0D0] text-[#9A9A9A]"
          >
            <div className="flex flex-col items-center">
              <MessageSquare className="w-5 h-5" />
              <span className="text-xs mt-1">Chat</span>
            </div>
          </TabsTrigger>
          <TabsTrigger
            value="closet"
            className="data-[state=active]:bg-transparent data-[state=active]:text-[#E8D0D0] text-[#9A9A9A]"
          >
            <div className="flex flex-col items-center">
              <ShoppingBag className="w-5 h-5" />
              <span className="text-xs mt-1">Closet</span>
            </div>
          </TabsTrigger>
        </TabsList>
      </Tabs>
    </div>
  )
}
