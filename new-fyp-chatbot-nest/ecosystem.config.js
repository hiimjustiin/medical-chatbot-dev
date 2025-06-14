module.exports = {
  apps: [
    {
      name: "chatbot-backend",
      script: "dist/main.js",
      env: {
        SUPABASE_URL: "https://dpexxrlylbwvwamekcoz.supabase.co",
        SUPABASE_SERVICE_ROLE_KEY: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRwZXh4cmx5bGJ3dndhbWVrY296Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NDg4MzUzNSwiZXhwIjoyMDYwNDU5NTM1fQ.vqh5O2Led2LLokHoD19NMGTHqgns_--JbKMUOogC1eI"
      }
    }
  ]
};
