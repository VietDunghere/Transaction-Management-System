import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { RouterProvider } from '@tanstack/react-router';
import './index.css';
import 'normalize.css';
import { GlobalStyles } from './components/GlobalStyles/GlobalStyles.tsx';
import { router } from './routes';

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <GlobalStyles>
            <RouterProvider router={router} />
        </GlobalStyles>
    </StrictMode>,
);
