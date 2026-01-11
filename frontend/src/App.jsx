import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import HomePage from './pages/HomePage';
import CreateMonitorPage from './pages/CreateMonitorPage';
import MonitorDetailPage from './pages/MonitorDetailPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="app">
          <header className="header">
            <div className="container">
              <h1>Exa Monitor</h1>
              <p className="subtitle">Monitor the web for new content</p>
            </div>
          </header>

          <main className="main">
            <div className="container">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/monitors/new" element={<CreateMonitorPage />} />
                <Route path="/monitors/:monitorId" element={<MonitorDetailPage />} />
              </Routes>
            </div>
          </main>

          <footer className="footer">
            <div className="container">
              <p>Powered by Exa AI & GPT-4</p>
            </div>
          </footer>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
