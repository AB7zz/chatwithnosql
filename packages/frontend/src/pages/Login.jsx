import { useState } from 'react';
import { auth, db } from '../firebase/config.js';
import { signInWithEmailAndPassword, createUserWithEmailAndPassword } from 'firebase/auth';
import { setDoc, doc } from 'firebase/firestore';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const Login = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [currentStep, setCurrentStep] = useState(1); // 1: auth, 2: company details
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [companyDetails, setCompanyDetails] = useState({
    name: '',
    address: '',
    phone: '',
    industry: '',
    size: '',
    dataLakeSource: '',
    credentialsFile: null
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleCompanyDetailsChange = (e) => {
    const { name, value } = e.target;
    setCompanyDetails(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCompanyDetails(prev => ({
        ...prev,
        credentialsFile: file
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      if (isLogin) {
        await signInWithEmailAndPassword(auth, email, password);
        navigate('/chat');
      } else {
        if (currentStep === 1) {
          if (password.length < 6) {
            setError('Password must be at least 6 characters long');
            return;
          }
          if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
          }
          setCurrentStep(2);
        } else {
          // Create user
          const userCredential = await createUserWithEmailAndPassword(auth, email, password);
          
          // Save company details to Firestore (without credentials file)
          const companyData = {
            name: companyDetails.name,
            address: companyDetails.address,
            phone: companyDetails.phone,
            industry: companyDetails.industry,
            size: companyDetails.size,
            userId: userCredential.user.uid,
            createdAt: new Date().toISOString()
          };
          
          await setDoc(doc(db, 'companies', userCredential.user.uid), companyData);

          // If Firebase is selected and credentials file exists, send to backend
          if (companyDetails.dataLakeSource === 'firebase' && companyDetails.credentialsFile) {
            const formData = new FormData();
            formData.append('credentials', companyDetails.credentialsFile);
            formData.append('company_id', userCredential.user.uid);

            try {
              await axios.post('http://localhost:5000/api/data-lake', formData, {
                headers: {
                  'Content-Type': 'multipart/form-data',
                },
              });
            } catch (error) {
              console.error('Error sending credentials:', error);
              // Show error but continue with navigation
              setError('Data lake setup failed, but account was created successfully');
            }
          }
          
          navigate('/chat');
        }
      }
    } catch (err) {
      if (err.code === 'auth/email-already-in-use') {
        setError('An account with this email already exists');
      } else if (err.code === 'auth/invalid-email') {
        setError('Please enter a valid email address');
      } else if (err.code === 'auth/weak-password') {
        setError('Password should be at least 6 characters');
      } else {
        setError(err.message);
      }
    }
  };

  const renderCompanyForm = () => (
    <>
      <div className="">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
          Company Details
        </h2>
      </div>
      <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
        {error && (
          <div className="text-red-500 text-sm text-center">
            {error}
          </div>
        )}
        
        <div>
          <label htmlFor="company-name" className="block text-sm font-medium text-white">
            Company Name
          </label>
          <input
            id="company-name"
            name="name"
            type="text"
            required
            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            value={companyDetails.name}
            onChange={handleCompanyDetailsChange}
          />
        </div>

        <div>
          <label htmlFor="address" className="block text-sm font-medium text-white">
            Address
          </label>
          <input
            id="address"
            name="address"
            type="text"
            required
            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            value={companyDetails.address}
            onChange={handleCompanyDetailsChange}
          />
        </div>

        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-white">
            Phone Number
          </label>
          <input
            id="phone"
            name="phone"
            type="tel"
            required
            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            value={companyDetails.phone}
            onChange={handleCompanyDetailsChange}
          />
        </div>

        <div>
          <label htmlFor="industry" className="block text-sm font-medium text-white">
            Industry
          </label>
          <select
            id="industry"
            name="industry"
            required
            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            value={companyDetails.industry}
            onChange={handleCompanyDetailsChange}
          >
            <option value="">Select Industry</option>
            <option value="technology">Technology</option>
            <option value="healthcare">Healthcare</option>
            <option value="retail">Retail</option>
            <option value="manufacturing">Manufacturing</option>
            <option value="finance">Finance</option>
            <option value="other">Other</option>
          </select>
        </div>

        <div>
          <label htmlFor="size" className="block text-sm font-medium text-white">
            Company Size
          </label>
          <select
            id="size"
            name="size"
            required
            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            value={companyDetails.size}
            onChange={handleCompanyDetailsChange}
          >
            <option value="">Select Size</option>
            <option value="1-10">1-10 employees</option>
            <option value="11-50">11-50 employees</option>
            <option value="51-200">51-200 employees</option>
            <option value="201-500">201-500 employees</option>
            <option value="500+">500+ employees</option>
          </select>
        </div>

        {/* Add Data Lake Source Selection */}
        <div>
          <label htmlFor="dataLakeSource" className="block text-sm font-medium text-white">
            Data Lake Source
          </label>
          <select
            id="dataLakeSource"
            name="dataLakeSource"
            required
            className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
            value={companyDetails.dataLakeSource}
            onChange={handleCompanyDetailsChange}
          >
            <option value="">Select Data Lake Source</option>
            <option value="firebase">Firebase Storage</option>
            <option value="aws" disabled>AWS S3 (Coming Soon)</option>
            <option value="azure" disabled>Azure Blob Storage (Coming Soon)</option>
          </select>
        </div>

        {/* Show file upload only if Firebase is selected */}
        {companyDetails.dataLakeSource === 'firebase' && (
          <div>
            <label htmlFor="credentials" className="block text-sm font-medium text-white">
              Firebase Credentials JSON
            </label>
            <input
              id="credentials"
              name="credentials"
              type="file"
              accept=".json"
              required
              onChange={handleFileChange}
              className="mt-1 block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-md file:border-0
                file:text-sm file:font-semibold
                file:bg-indigo-50 file:text-indigo-700
                hover:file:bg-indigo-100"
            />
            <p className="mt-1 text-sm text-gray-500">
              Please upload your Firebase service account credentials JSON file
            </p>
          </div>
        )}

        <div className="flex space-x-4">
          <button
            type="button"
            onClick={() => setCurrentStep(1)}
            className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-900 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Back
          </button>
          <button
            type="submit"
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Complete Registration
          </button>
        </div>
      </form>
    </>
  );

  return (
    <div className="py-20 min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 to-gray-800">
      <div className="max-w-md w-full space-y-8 p-8 bg-gray-800 rounded-lg shadow-md">
        {/* Show toggle buttons only on first step or login */}
        {(isLogin || currentStep === 1) && (
          <div className="flex justify-center space-x-4 mb-8">
            <button
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                isLogin
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-500 hover:text-indigo-600'
              }`}
              onClick={() => {
                setIsLogin(true);
                setCurrentStep(1);
              }}
            >
              Sign In
            </button>
            <button
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                !isLogin
                  ? 'bg-indigo-600 text-white'
                  : 'text-gray-500 hover:text-indigo-600'
              }`}
              onClick={() => {
                setIsLogin(false);
                setCurrentStep(1);
              }}
            >
              Register
            </button>
          </div>
        )}

        {/* Show either auth form or company details form */}
        {(!isLogin && currentStep === 2) ? renderCompanyForm() : (
          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="text-red-500 text-sm text-center">
                {error}
              </div>
            )}
            
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="sr-only">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            {/* Confirm Password Field (Only for Register) */}
            {!isLogin && (
              <div>
                <label htmlFor="confirm-password" className="sr-only">
                  Confirm Password
                </label>
                <input
                  id="confirm-password"
                  name="confirmPassword"
                  type="password"
                  required
                  className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-white bg-gray-800 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                  placeholder="Confirm Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                />
              </div>
            )}

            {/* Submit Button */}
            <div>
              <button
                type="submit"
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                {isLogin ? 'Sign in' : 'Create Account'}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default Login;
