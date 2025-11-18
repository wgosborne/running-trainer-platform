# Running Tracker Frontend

React frontend for the Running Tracker application. Built with React, TypeScript, Vite, and Tailwind CSS.

## Features

- User authentication (login/register)
- Training plan management
- Workout tracking
- Run logging and viewing
- PDF import for training plans
- Strava integration for automatic run syncing

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Fetch API** - HTTP client

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install
```

### Development

```bash
# Start development server
npm run dev

# Application will be available at http://localhost:5173
```

The dev server includes proxy configuration to forward API requests to the backend at `http://localhost:8000`.

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── pages/           # Page components
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── PlanDetail.tsx
│   │   ├── ImportPDF.tsx
│   │   └── StravaAuth.tsx
│   ├── components/      # Reusable components
│   │   ├── Header.tsx
│   │   ├── PlanCard.tsx
│   │   └── RunList.tsx
│   ├── api.ts          # API client
│   ├── store.ts        # State management
│   ├── types.ts        # TypeScript types
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles
├── public/             # Static assets
├── index.html          # HTML template
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── Dockerfile
```

## Pages

### Login
- User registration and login
- Form validation
- Error handling

### Dashboard
- View all training plans
- Create new plans
- Quick access to PDF import and Strava sync
- Plan overview with progress

### Plan Detail
- View plan information
- List workouts and runs
- Add manual runs
- View workout completion status
- Import workouts from PDF

### Import PDF
- Upload PDF training plans
- Select target plan
- Progress feedback
- Success/error messages

### Strava Auth
- Authorize Strava connection
- Sync recent runs
- Select target plan
- View sync status

## Components

### Header
- Navigation
- User info
- Logout button

### PlanCard
- Plan summary
- Status badge
- Progress bar
- Click to view details

### RunList
- Table of runs
- Distance and pace display
- Source indicator (manual/Strava)

## State Management

Uses Zustand for simple, lightweight state management:

- User authentication state
- Training plans
- Runs
- Current selected plan

## API Integration

All API calls go through the centralized API client (`api.ts`) which handles:
- Request formatting
- Error handling
- Authentication headers
- Response parsing

API base URL is configurable via `VITE_API_URL` environment variable.

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Docker

### Build

```bash
docker build -t running-tracker-frontend .
```

### Run

```bash
docker run -p 80:80 running-tracker-frontend
```

## Running with Docker Compose

From the project root:

```bash
docker-compose up frontend
```

## User Flow

1. **Login/Register** - Create account or login
2. **Dashboard** - View all plans, create new plan
3. **Import PDF** - Upload training plan PDF
4. **Authorize Strava** - Connect Strava account
5. **Sync Runs** - Import runs from Strava
6. **View Plan Details** - See workouts and completed runs
7. **Log Runs** - Manually add runs

## Styling

Uses Tailwind CSS utility classes for styling. Key design elements:

- Blue primary color scheme
- Clean, modern interface
- Responsive layout
- Card-based design
- Clear visual hierarchy

## Type Safety

Full TypeScript coverage with:
- Interface definitions for all data models
- Type-safe API client
- Strict mode enabled
- No implicit any

## Future Enhancements

- Local storage for persistence
- Advanced filtering and sorting
- Charts and analytics
- Mobile responsive improvements
- Dark mode
- Notifications
- Workout calendar view
