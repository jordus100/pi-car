import {useContext, useEffect} from "react";
import {AuthContext, AuthProvider} from "./services/AuthProvider";
import {BrowserRouter, Route, Router, Routes} from "react-router-dom";
import LoginPage from "./Login";
import ProtectedRoute from "./ProtectedRoute";
import MainPage from "./MainPage";

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
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;