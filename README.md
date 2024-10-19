# Conqueria Caps - Backend _(IN PROGRESS)_

## About the Game
**Conqueria Caps** is a real-time, strategy-based board game where 2-6 players battle for dominance over territories on a dynamic world map. Each player begins with an equal amount of resources, and they must make strategic decisions to generate income, fortify their defenses, or launch calculated attacks on their opponents. The game spans multiple continents, with cities, outposts, and military units playing pivotal roles in achieving victory. Players can capture territories, deploy defensive structures, launch attack waves, and strategically manage resources to win by capturing enemy capitals or controlling the most land.

Conqueria Caps also features premium in-game options, including exclusive emotes, customizable cosmetics, and premium troops/buildings, ensuring no pay-to-win mechanics.

This repository contains the **backend** source code for **Conqueria Caps**, developed using **FastAPI**, with real-time WebSocket functionality, PostgreSQL for the database, and Redis for caching and real-time updates.

### Target Features

- **User Authentication**: Secure user login using JWT and OAuth (Google, Facebook, Steam).
- **Game State Management**: Handle turn-based strategy mechanics with real-time updates.
- **In-Game Actions**: Manage player actions like generating money, fortifying defenses, and launching attacks.
- **Matchmaking and Game Lobby**: Real-time matchmaking and lobby management with WebSocket communication.
- **Leaderboard and Ranking System**: Track player stats, skill points, and rank updates based on game results.
- **Premium Features**: Integration with Chargebee for subscription management and Stripe for in-game purchases.
- **Caching**: Redis caching for optimized performance.
- **Real-time Communication**: WebSocket-powered in-game chat for player alliances and lobby discussions.

---

## FastAPI Project Documentation

This project is a **FastAPI**-based backend for the strategy board game, with PostgreSQL as the database, Redis as the caching system, and pgAdmin4 for database management. The app is designed with scalability and multi-environment support, utilizing Docker Compose for orchestration, PostgreSQL for data storage, and Redis for caching. The application supports development, testing, and production environments, each with specific configuration files.

---

### Technology Stack
- **Backend Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Database Management**: pgAdmin4
- **Containerization**: Docker and Docker Compose
- **Environment Configuration**: `.env` files for DEV, TEST, and PROD environments

---

### Environment Configuration

The application uses environment-specific configuration files to manage credentials and settings for development, testing, and production environments.

**Environment Files:**
- **`.env.dev`**: Stores environment variables for development.
- **`.env.test`**: Stores environment variables for testing.
- **`.env.prod`**: Stores environment variables for production.
  
**Example `.env` files are included in GitHub**:
- `.env.dev.example`
- `.env.test.example`
- `.env.prod.example`

These files provide the correct structure with placeholder values for each environment. It is imperative to create these files from their respective example files before proceeding with the app installation.

---

## API Documentation

The backend uses **FastAPI's automatic interactive documentation**.

- Visit the **Swagger UI** at: `http://127.0.0.1:8000`
- Visit the **Redoc documentation** at: `http://127.0.0.1:8000/redoc`

These pages provide detailed information about all available endpoints, their request parameters, and response formats.

---

### Docker Setup

The project uses Docker Compose to orchestrate services (FastAPI app, PostgreSQL, Redis, pgAdmin).

#### Docker Services:
- **web**: FastAPI application container.
- **db**: PostgreSQL database container.
- **redis**: Redis caching container.
- **pgadmin**: pgAdmin4 container for managing PostgreSQL databases.

### Running the Application (DEV Environment)

After first creating `.env.dev`, to start the application with Docker Compose:

1. **Build and run the services**:
   ```bash
   docker-compose up
   ```

2. **Access the services**:
   - **FastAPI App**: `http://localhost:8000`
   - **pgAdmin4**: `http://localhost:5050` (can be accessed from the credentials specified in `.env.dev`)
   - **PostgreSQL**: Can be accessed from pgAdmin4 the credentials specified in `.env.dev`.
---

### Database Migrations (Using Alembic) 

We are using **Alembic** to handle database schema migrations. Alembic allows us to track changes in the database schema over time and apply them consistently across different environments (development, testing, production).

#### 1. Generating a New Migration

Whenever you make changes to your models and want to reflect those changes in the database schema, you need to generate a migration script.
   ```bash
   docker-compose exec web alembic revision --autogenerate -m "<migration message>"
   ```

   This command will generate a new migration script in the `alembic/versions` directory based on the differences between the current state of your database and the state of your SQLAlchemy models. The `-m` flag allows you to provide a message for the migration (e.g., "create initial tables").

#### 2. Applying the Migration

After generating a migration, you need to apply it to your database to update its schema.
   ```bash
   docker-compose exec web alembic upgrade head
   ```

   This command will apply the latest migration(s) to your database. The `head` argument ensures that all migrations up to the latest one are applied.

---

### **pgAdmin4 Configuration**

To manage the PostgreSQL database with **pgAdmin4**:
1. Open `http://localhost:5050` in your browser.
2. Log in with:
   - **Email**: `admin@example.com`
   - **Password**: `admin`
3. Add a new server:
   - **Host**: `db`
   - **Port**: `5432`
   - **Username**: `postgres`
   - **Password**: `devpassword`

This allows you to view and manage your PostgreSQL database in pgAdmin4.

---

### **Next Steps**
1. **Development**: Continue adding business logic and endpoints to the FastAPI app. Use `.env.dev`.
2. **Testing**: Set up unit tests and integration tests. Use `.env.test`.
3. **Production**: Finalize the production environment and ensure the configurations are production-ready using `.env.prod`.

---

## Target Apps (To Be Developed)

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Conqueria Caps** is still evolving! Contributions, bug reports, and feature requests are welcome.
