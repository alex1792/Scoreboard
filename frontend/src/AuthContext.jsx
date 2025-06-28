import { createContext } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children, currentUser, setCurrentUser }) {
  return (
    <AuthContext.Provider value={{ currentUser, setCurrentUser }}>
      {children}
    </AuthContext.Provider>
  );
}
