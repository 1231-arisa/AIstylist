# AIstylist Landing Page - Setup Instructions

This is a Next.js application with integrated AI fashion styling features including Google OAuth, Stripe payments, weather API, and AI-powered outfit recommendations.

## Features Implemented

✅ **Google OAuth Authentication** - Users can sign in with their Google account
✅ **Stripe Payment Integration** - $20/month subscription after free trial
✅ **Weather API Integration** - Real-time weather data displayed on home screen
✅ **AI Outfit Recommendations** - Generates 2 outfit combinations from closet items
✅ **Chat API with Image Upload** - TPO-based fashion advice with image analysis
✅ **Automatic Image Saving** - User-uploaded images are automatically saved and analyzed
✅ **Database Integration** - PostgreSQL with Prisma ORM for user data and subscriptions

## Prerequisites

- Node.js 18+ 
- PostgreSQL database
- Google OAuth credentials
- Stripe account
- OpenAI API key
- Weather API key

## Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Set up environment variables:**
   Create a `.env.local` file with the following variables:
   ```env
   # Database
   DATABASE_URL="postgresql://username:password@localhost:5432/aistylist?schema=public"

   # NextAuth
   NEXTAUTH_URL="http://localhost:3000"
   NEXTAUTH_SECRET="your-secret-key-here"

   # Google OAuth
   GOOGLE_CLIENT_ID="your-google-client-id"
   GOOGLE_CLIENT_SECRET="your-google-client-secret"

   # Stripe
   STRIPE_PUBLISHABLE_KEY="pk_test_..."
   STRIPE_SECRET_KEY="sk_test_..."
   STRIPE_WEBHOOK_SECRET="whsec_..."

   # OpenAI
   OPENAI_API_KEY="sk-..."

   # Weather API
   WEATHER_API_KEY="your-weather-api-key"

   # File Upload
   UPLOAD_DIR="./uploads"
   ```

3. **Set up the database:**
   ```bash
   npx prisma generate
   npx prisma db push
   ```

4. **Create uploads directory:**
   ```bash
   mkdir uploads
   ```

## API Setup

### Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add authorized redirect URIs: `http://localhost:3000/api/auth/callback/google`

### Stripe Setup
1. Create a [Stripe account](https://stripe.com/)
2. Get your API keys from the dashboard
3. Create a product and price for $20/month subscription
4. Update the price ID in `lib/stripe.ts`
5. Set up webhook endpoint: `http://localhost:3000/api/stripe/webhook`

### OpenAI Setup
1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to environment variables

### Weather API Setup
1. Sign up for [WeatherAPI](https://www.weatherapi.com/)
2. Get your API key
3. Add to environment variables

## Running the Application

1. **Start the development server:**
   ```bash
   npm run dev
   ```

2. **Open your browser:**
   Navigate to `http://localhost:3000`

## Usage

1. **Sign in** with Google OAuth
2. **Free trial** - Users get 7 days free access to all features
3. **Weather integration** - Current weather is displayed on the home screen
4. **Outfit recommendations** - AI generates 2 outfit combinations based on weather and closet items
5. **Chat functionality** - Upload images or ask questions for fashion advice
6. **Subscription** - After trial, users must subscribe for $20/month to continue

## File Structure

```
├── app/
│   ├── api/
│   │   ├── auth/[...nextauth]/route.ts
│   │   ├── chat/route.ts
│   │   ├── outfits/route.ts
│   │   ├── stripe/
│   │   └── weather/route.ts
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── auth-provider.tsx
│   └── ui/
├── lib/
│   ├── auth.ts
│   ├── database.ts
│   ├── outfit-recommendations.ts
│   ├── stripe.ts
│   ├── subscription.ts
│   └── weather.ts
├── prisma/
│   └── schema.prisma
└── uploads/
```

## Database Schema

The application uses PostgreSQL with the following main tables:
- `User` - User accounts and profile information
- `Subscription` - Subscription status and Stripe integration
- `Outfit` - Generated outfit recommendations
- `ChatMessage` - Chat conversation history
- `UploadedImage` - User-uploaded images with AI analysis
- `WeatherCache` - Cached weather data

## Deployment

1. **Deploy to Vercel:**
   ```bash
   vercel
   ```

2. **Set up production environment variables** in Vercel dashboard

3. **Set up production database** (recommend using Vercel Postgres or Supabase)

4. **Update webhook URLs** for Stripe and Google OAuth

## Troubleshooting

- **Database connection issues**: Check DATABASE_URL format
- **OAuth errors**: Verify redirect URIs match exactly
- **Stripe webhook failures**: Check webhook secret and endpoint URL
- **Image upload issues**: Ensure uploads directory exists and has write permissions
- **Weather API errors**: Verify API key and rate limits

## Support

For issues or questions, please check the console logs and ensure all environment variables are properly set.
