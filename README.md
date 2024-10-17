# Conqueria Caps - Backend _(IN PROGRESS)_

### About the Game
**Conqueria Caps** is a real-time, strategy-based board game where 2-6 players battle for dominance over territories on a dynamic world map. Each player begins with an equal amount of resources, and they must make strategic decisions to generate income, fortify their defenses, or launch calculated attacks on their opponents. The game spans multiple continents, with cities, outposts, and military units playing pivotal roles in achieving victory. Players can capture territories, deploy defensive structures, launch attack waves, and strategically manage resources to win by capturing enemy capitals or controlling the most land.

Conqueria Caps also features premium in-game options, including exclusive emotes, customizable cosmetics, and premium troops/buildings, ensuring no pay-to-win mechanics.

This repository contains the **backend** source code for **Conqueria Caps**, developed using **FastAPI**, with real-time WebSocket functionality, PostgreSQL for the database, and Redis for caching and real-time updates.

---

## Features

- **User Authentication**: Secure user login using JWT and OAuth (Google, Facebook, Steam).
- **Game State Management**: Handle turn-based strategy mechanics with real-time updates.
- **In-Game Actions**: Manage player actions like generating money, fortifying defenses, and launching attacks.
- **Matchmaking and Game Lobby**: Real-time matchmaking and lobby management with WebSocket communication.
- **Leaderboard and Ranking System**: Track player stats, skill points, and rank updates based on game results.
- **Premium Features**: Integration with Chargebee for subscription management and Stripe for in-game purchases.
- **Caching**: Redis caching for optimized performance.
- **Real-time Communication**: WebSocket-powered in-game chat for player alliances and lobby discussions.

---

## Installation

### Prerequisites

- **Python 3.8+**
- **PostgreSQL** (version 12+)
- **Redis**
- **Docker** (for containerization, optional but recommended)
- **Git**

### Steps to Install

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/conqueria-caps-backend.git
   cd conqueria-caps-backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   Create a `.env` file in the root directory of the project with the following variables:

   ```bash
   DATABASE_URL=postgresql://<username>:<password>@<hostname>:<port>/<database_name>
   REDIS_URL=redis://<hostname>:<port>
   SECRET_KEY=<your_secret_key>
   JWT_ALGORITHM=HS256
   OAUTH_GOOGLE_CLIENT_ID=<your_google_client_id>
   OAUTH_GOOGLE_CLIENT_SECRET=<your_google_client_secret>
   OAUTH_FACEBOOK_CLIENT_ID=<your_facebook_client_id>
   OAUTH_FACEBOOK_CLIENT_SECRET=<your_facebook_client_secret>
   OAUTH_STEAM_API_KEY=<your_steam_api_key>
   STRIPE_SECRET_KEY=<your_stripe_secret_key>
   CHARGEBEE_SITE=<your_chargebee_site>
   CHARGEBEE_API_KEY=<your_chargebee_api_key>
   ```

5. **Set up the database**:
   Ensure that PostgreSQL is running and create the necessary database:

   ```sql
   CREATE DATABASE conqueria_caps;
   ```

   Then apply migrations to set up the database schema:

   ```bash
   alembic upgrade head
   ```

6. **Run the development server**:
   Start the FastAPI backend server:

   ```bash
   uvicorn app.main:app --reload
   ```

   The server will be accessible at `http://127.0.0.1:8000/`.

---

## Docker Setup (Optional)

You can run the entire backend using Docker for easier deployment and environment setup.

1. **Build the Docker image**:
   ```bash
   docker build -t conqueria-caps-backend .
   ```

2. **Run the Docker container**:
   ```bash
   docker run -d --name conqueria_backend -p 8000:8000 conqueria-caps-backend
   ```

This will start the backend on `http://localhost:8000`.

---

## Included Apps

### **1. User Management**
   - **Authentication**: JWT-based login, registration, and social OAuth logins (Google, Facebook, Steam).
   - **Profile Management**: Manage user profiles, including skill points, rank, and premium status.
   - **Session Management**: Persistent user sessions with token-based authentication.

### **2. Game Setup and Matchmaking**
   - **Game Creation**: API to create new games with customizable settings (map, turn time, max game time, fog of war, etc.).
   - **Matchmaking**: Automatically match players into open game slots based on rank and skill points.
   - **Lobby Management**: Real-time WebSocket-powered lobby management where players can join, leave, and chat.

### **3. In-Game Actions**
   - **Generate**: Build industrial plants, factories, and other structures to generate resources over turns.
   - **Fortify**: Build or upgrade defensive buildings like gunners, flame throwers, and anti-tank cannons.
   - **Attack**: Launch waves of attacking units (troops, tanks, air units) towards enemy cities and territories.

### **4. Game State Management**
   - **Turn-Based State**: Handle player turns, synchronize game state between players in real time.
   - **City and Territory Management**: Manage the health and ownership of cities, outposts, and territories.
   - **Attack Simulation**: Run combat simulations to calculate attack results based on player actions.

### **5. Leaderboards and Rankings**
   - **Global Leaderboard**: Display player rankings based on wins, skill points, and captured territories.
   - **Skill Points Calculation**: Award skill points based on game results and update the player's rank accordingly.

### **6. Premium Features**
   - **Tokens and Gems**: Manage tokens (for starting games) and gems (for in-game purchases and premium features).
   - **Subscription Management**: Integration with Chargebee for monthly subscriptions and premium feature management.
   - **Payment Integration**: Stripe integration for purchasing gems, battle passes, and premium cosmetic features.

### **7. Real-time Communication**
   - **WebSocket-powered Chat**: Players can communicate during games via chat, with chat permissions restricted to premium players where applicable.
   - **Lobby Chat**: Players can chat while waiting in the lobby for the game to start.

### **8. Game Analytics and Logging**
   - **Player Action Tracking**: Track key in-game actions for analytics purposes.
   - **Error Logging**: Log errors and performance issues for debugging and troubleshooting.

---

## API Documentation

The backend uses **FastAPI's automatic interactive documentation**.

- Visit the **Swagger UI** at: `http://127.0.0.1:8000/docs`
- Visit the **Redoc documentation** at: `http://127.0.0.1:8000/redoc`

These pages provide detailed information about all available endpoints, their request parameters, and response formats.

---

## Testing

You can run automated tests to ensure the backend functions correctly. To run the test suite:

1. **Install test dependencies**:
   ```bash
   pip install -r test-requirements.txt
   ```

2. **Run the tests**:
   ```bash
   pytest
   ```

Test coverage includes user management, game state management, in-game actions, and more.

---

## Deployment

For production deployment, the backend can be hosted using services like **Render**, **AWS EC2**, or **Heroku**.

1. **Set up environment variables** using the `.env` file (or a similar approach depending on your hosting provider).
2. **Build and deploy the Docker container** (if using Docker).
3. Ensure SSL is configured using **Nginx** with **Let’s Encrypt** for HTTPS deployment.

---

## Contributing

1. Fork the repository.
2. Create a new feature branch: `git checkout -b feature-name`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push the branch: `git push origin feature-name`.
5. Submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Conqueria Caps** is still evolving! Contributions, bug reports, and feature requests are welcome.
