import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { Database, Search, MessageSquare, Brain, ArrowRight } from 'lucide-react';

gsap.registerPlugin(ScrollTrigger);

const Home = () => {
  const navigate = useNavigate();
  const heroRef = useRef(null);
  const featuresRef = useRef(null);
  const useCasesRef = useRef(null);

  useEffect(() => {
    // Reset any existing animations
    gsap.set(heroRef.current.children, { clearProps: "all" });
    gsap.set(".feature-card", { clearProps: "all" });
    gsap.set(".use-case", { clearProps: "all" });

    // Hero section animation with higher opacity
    gsap.from(heroRef.current.children, {
      duration: 1,
      y: 100,
      opacity: 0,
      stagger: 0.2,
      ease: "power3.out",
      force3D: true, // Improves performance
      clearProps: "all" // Ensures final state is clean
    });

    // Features section animation
    gsap.from(".feature-card", {
      scrollTrigger: {
        trigger: featuresRef.current,
        start: "top center+=100",
        toggleActions: "play none none reverse"
      },
      duration: 0.8,
      y: 50,
      opacity: 0,
      stagger: 0.2,
      ease: "power2.out",
      force3D: true,
      clearProps: "all"
    });

    // Use cases animation
    gsap.from(".use-case", {
      scrollTrigger: {
        trigger: useCasesRef.current,
        start: "top center+=100",
        toggleActions: "play none none reverse"
      },
      duration: 0.8,
      x: -50,
      opacity: 0,
      stagger: 0.3,
      ease: "power2.out",
      force3D: true,
      clearProps: "all"
    });
  }, []);

  const features = [
    {
      icon: <Database className="w-8 h-8" />,
      title: "Data Lake Integration",
      description: "Connect seamlessly with your existing data infrastructure"
    },
    {
      icon: <Search className="w-8 h-8" />,
      title: "Natural Language Search",
      description: "Find information using simple, conversational queries"
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: "AI-Powered Analysis",
      description: "Get intelligent insights from your data automatically"
    }
  ];

  const useCases = [
    {
      title: "Customer Support",
      description: "Search through support emails to improve response times and service quality",
      color: "from-blue-500 to-cyan-500"
    },
    {
      title: "Legal Documents",
      description: "Analyze contracts and legal documents for faster decision making",
      color: "from-purple-500 to-pink-500"
    },
    {
      title: "Business Intelligence",
      description: "Extract valuable insights from your company's data lake",
      color: "from-orange-500 to-red-500"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800">
      {/* Hero Section */}
      <div 
        ref={heroRef}
        className="min-h-[90vh] flex flex-col items-center justify-center text-center px-4 relative overflow-hidden"
      >
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ 
            scale: [1, 1.2, 1],
            rotate: [0, 360],
            opacity: 1
          }}
          transition={{ duration: 2 }}
          className="absolute w-96 h-96 bg-blue-500/10 rounded-full blur-3xl -z-10"
        />
        
        <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 text-transparent bg-clip-text mb-6 opacity-100">
          Enterprise Search,
          <br />
          Simplified
        </h1>
        
        <p className="text-xl text-gray-300 max-w-2xl mb-12 opacity-100">
          Empower your team to find and analyze information across your entire data lake
          using natural language queries
        </p>

        <motion.button
          initial={{ opacity: 1 }}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => navigate('/choose')}
          className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white px-8 py-4 rounded-lg font-medium text-lg flex items-center space-x-2 hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-200"
        >
          <span>Get Started</span>
          <ArrowRight className="w-5 h-5" />
        </motion.button>
      </div>

      {/* Features Section */}
      <div ref={featuresRef} className="py-24 px-4">
        <h2 className="text-4xl font-bold text-center text-white mb-16 opacity-100">
          Powerful Features
        </h2>
        
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="feature-card bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:bg-gray-800/80 transition-colors duration-300"
              style={{ opacity: 1 }} // Ensure initial opacity is 1
            >
              <div className="bg-blue-500/10 w-16 h-16 rounded-lg flex items-center justify-center text-blue-400 mb-4">
                {feature.icon}
              </div>
              <h3 className="text-xl font-bold text-white mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-400">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Use Cases Section */}
      <div ref={useCasesRef} className="py-24 px-4 bg-gray-900/50">
        <h2 className="text-4xl font-bold text-center text-white mb-16 opacity-100">
          Use Cases
        </h2>
        
        <div className="max-w-7xl mx-auto space-y-8">
          {useCases.map((useCase, index) => (
            <div 
              key={index}
              className="use-case bg-gradient-to-r border border-gray-700/50 rounded-xl p-8 hover:scale-[1.02] transition-transform duration-300"
              style={{ opacity: 1 }} // Ensure initial opacity is 1
            >
              <h3 className={`text-2xl font-bold bg-gradient-to-r ${useCase.color} text-transparent bg-clip-text mb-4`}>
                {useCase.title}
              </h3>
              <p className="text-gray-300">
                {useCase.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Home;