# Transaction Management System - Frontend

Admin Dashboard & Case Management interface for the Banking Transaction Management System. Built with React 19, TypeScript, Vite, and Tailwind CSS.

## Yêu Cầu Hệ Thống

- **Node.js**: v18.0.0+ (Khuyến nghị: v20.x LTS hoặc v22.x)
- **Package Manager**: npm (Khuyến nghị: v9+)
- **OS**: Windows, macOS, Linux

## Cài Đặt & Setup

### 1. Clone Repository và Cài Đặt Dependencies

```bash
# Clone repository
git clone <repository-url>
cd Transaction-Management-System/frontend

# Cài đặt dependencies
npm install
```

### 2. Cấu Hình Environment

Tạo file `.env.local` trong thư mục `frontend/`:

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT=30000

# Application
VITE_APP_NAME=Transaction Management System
VITE_APP_VERSION=1.0.0
```

> **Lưu ý**: File `.env.local` không được commit lên git. Nó chỉ dùng cho local development.

## Các Lệnh Phát Triển

### Development Server

```bash
npm run dev
# Server chạy tại http://localhost:5173
```

### Build Production

```bash
npm run build
# Output: dist/
# Bước này sẽ:
# 1. Type-check với TypeScript (tsc -b)
# 2. Bundle code với Vite
# 3. Minify & optimize cho production
```

### Preview Production Build

```bash
npm run preview
# Xem trước build production tại http://localhost:4173
```

### Linting & Code Quality

```bash
# Chạy ESLint check
npm run lint

# Fix ESLint issues tự động
npm run lint -- --fix
```

### Testing

```bash
# Chạy tất cả tests một lần
npm test

# Watch mode - tự động re-run khi code thay đổi
npm run test:watch
```

### Generate/Codegen

```bash
# Chạy các script codegen (routes, types, etc.)
npm run gc
```

## Cấu Trúc Dự Án

```
frontend/
├── src/
│   ├── api/              # API services & queries (axios, TanStack Query)
│   ├── assets/           # Static files (images, fonts, etc.)
│   ├── components/       # Reusable UI components
│   ├── hooks/            # Custom React hooks
│   ├── layouts/          # Page layouts
│   ├── lib/              # Utility libraries & helpers
│   ├── pages/            # Page components
│   ├── routes/           # TanStack Router configuration
│   ├── services/         # Business logic services
│   ├── stores/           # Zustand state stores
│   ├── test/             # Test utilities & setup
│   ├── types/            # TypeScript types & interfaces
│   ├── utils/            # Utility functions
│   ├── App.tsx           # Root component
│   ├── index.css         # Global styles
│   └── main.tsx          # Entry point
├── public/               # Public assets
├── docs/                 # Project documentation
├── scripts/              # Build & utility scripts
├── index.html            # HTML template
├── vite.config.ts        # Vite configuration
├── eslint.config.js      # ESLint configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Project metadata & dependencies
```

## Tech Stack

| Layer             | Technology             | Version |
| ----------------- | ---------------------- | ------- |
| **Runtime**       | Node.js                | 18+     |
| **Framework**     | React                  | 19.x    |
| **Language**      | TypeScript             | 6.x     |
| **Build**         | Vite                   | 8.x     |
| **Styling**       | Tailwind CSS           | 4.x     |
| **State**         | Zustand                | 5.x     |
| **Routing**       | TanStack Router        | 1.x     |
| **Data Fetching** | TanStack Query         | 5.x     |
| **API Client**    | Axios                  | 1.x     |
| **Forms**         | React Hook Form        | 7.x     |
| **Validation**    | Zod                    | 4.x     |
| **Charts**        | ECharts, Recharts      | Latest  |
| **Testing**       | Vitest                 | 4.x     |
| **Linting**       | ESLint                 | 9.x     |
| **Compiler**      | React Compiler (Babel) | 1.x     |

## Key Dependencies

### Production

- **@tanstack/react-query**: Server state management, caching, synchronization
- **@tanstack/react-router**: Type-safe routing
- **zustand**: Client state management
- **react-hook-form**: Efficient form handling
- **axios**: HTTP client
- **echarts, recharts**: Data visualization
- **lucide-react**: Icon library
- **zod**: Schema validation

### Development

- **vite**: Fast build tool
- **typescript**: Type safety
- **eslint + typescript-eslint**: Code quality
- **vitest**: Unit testing
- **@testing-library/react**: Testing utilities

## Workflow

### Phát Triển Tính Năng

1. **Tạo nhánh mới**

    ```bash
    git checkout -b feature/your-feature-name
    ```

2. **Chạy development server**

    ```bash
    npm run dev
    ```

3. **Code với type-checking & hot reload**
    - Mở http://localhost:5173
    - IDE sẽ hiển thị type errors ngay lập tức
    - Mỗi lần save tự động reload page

4. **Kiểm tra code quality**

    ```bash
    npm run lint
    npm test
    ```

5. **Build & test production**

    ```bash
    npm run build
    npm run preview
    ```

6. **Commit & Push**
    ```bash
    git add .
    git commit -m "feat: add your feature"
    git push origin feature/your-feature-name
    ```

## Testing

### Unit & Integration Tests

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage report
npm test -- --coverage
```

Test files nằm cùng với source code:

- `*.test.ts` - Unit tests
- `*.test.tsx` - Component tests
- `test/` folder - Test utilities & setup

### Testing Library

- **@testing-library/react**: Component testing
- **@testing-library/user-event**: User interaction simulation
- **jsdom**: DOM environment

## Code Quality

### TypeScript Strict Mode

- Enabled by default
- Check `tsconfig.json` để configure

### ESLint Rules

- React best practices
- Hook rules enforcement
- Import sorting
- Type safety

## Documentation

- [API Design](./docs/API_DESIGN.md)
- [Project Convention](./docs/CONVENTION.md)
- [Project Structure](./docs/CONTEXT.md)
- [Test Results](./docs/TEST_RESULT.md)

## Troubleshooting

### Port 5173 đã bị sử dụng?

```bash
# Chỉ định port khác
npm run dev -- --port 3000
```

### Clear cache & reinstall

```bash
rm -rf node_modules package-lock.json
npm install
```

### TypeScript errors không disappear?

```bash
# Rebuild TypeScript
npm run build
```

### ESLint cache issue?

```bash
# Clear ESLint cache
npx eslint --cache --cache-strategy content
```

## Environment Setup Checklist

- [ ] Node.js version v18+
- [ ] Dependencies installed (`npm install`)
- [ ] `.env.local` created (if needed)
- [ ] Backend API running on `http://localhost:8000`
- [ ] Development server starts without errors (`npm run dev`)
- [ ] No TypeScript errors in IDE
- [ ] Tests pass (`npm test`)
- [ ] Linting passes (`npm run lint`)

## Commit Conventions

```
feat: Add new feature
fix: Bug fix
refactor: Code refactoring
docs: Documentation update
test: Add/update tests
chore: Maintenance tasks
```

## Contributing

1. Follow the project conventions in `docs/CONVENTION.md`
2. Write tests for new features
3. Ensure all tests pass and linting is clean
4. Create a descriptive commit message
5. Submit a pull request

## Support & Questions

Tham khảo tài liệu dự án:

- [System Workflow](../docs/SYSTEM_WORKFLOW.md)
- [Database Setup](../docs/DATABASE_SETUP.md)
- [API Documentation](./docs/API_DESIGN.md)
