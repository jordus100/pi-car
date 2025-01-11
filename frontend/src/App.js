import {useContext, useEffect} from "react";
import {AuthContext, AuthProvider} from "./services/AuthProvider";
import {BrowserRouter, Route, Router, Routes} from "react-router-dom";
import LoginPage from "./Login";
import ProtectedRoute from "./ProtectedRoute";
import MainPage from "./MainPage";
import Settings from "./settings/Settings";

function App() {
  useEffect(() => {
    document.title = 'Robot remote control'
  }, []);
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedRoute />}>
            <Route path="/" element={<MainPage />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;