import { useAuth } from 'react-oidc-context';
import { LogIn } from 'lucide-react';

export const LoginButton = () => {
    const auth = useAuth();

    if (auth.isAuthenticated) {
        return null;
    }

    return (
        <button
            onClick={() => auth.signinRedirect()}
            className="flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700 transition-colors"
        >
            <LogIn size={18} />
            <span>Sign In</span>
        </button>
    );
};
