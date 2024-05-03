# Build
docker build -t avidito/revirathya-telegram-bot .

# Run (Manually Create .env)
docker run --name rvr-tel-bot -d --restart always --env-file .env avidito/revirathya-telegram-bot