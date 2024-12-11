import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { FaArrowRight } from 'react-icons/fa'

const Choose = () => {
  const [hoveredWarehouse, setHoveredWarehouse] = useState(null)

  const dataWarehouses = [
    { 
      name: 'Snowflake', 
      logo: 'https://companieslogo.com/img/orig/SNOW-35164165.png?t=1720244494',
      description: 'Cloud-native data platform offering scalability and performance',
      color: 'from-blue-400 to-blue-600'
    },
    { 
      name: 'Amazon Redshift', 
      logo: 'https://cdn.prod.website-files.com/625447c67b621ab49bb7e3e5/6511e6855e26e61247127ecb_63bdba82fbba1214de98c30d_1862px-Amazon-Redshift-Logo.svg%255B1%255D.png',
      description: 'Fast, simple, cost-effective data warehousing',
      color: 'from-orange-400 to-red-600'
    },
    { 
      name: 'Google BigQuery', 
      logo: 'https://cdn.worldvectorlogo.com/logos/google-bigquery-logo-1.svg',
      description: 'Serverless, highly scalable, and cost-effective',
      color: 'from-green-400 to-blue-500'
    },
  ]

  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 flex flex-col items-center justify-center p-8"
    >
      <motion.h1 
        initial={{ y: -50 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100 }}
        className="text-4xl font-bold mb-4 text-white text-center"
      >
        Choose Your Data Warehouse
      </motion.h1>
      <motion.p 
        initial={{ y: -30 }}
        animate={{ y: 0 }}
        transition={{ type: "spring", stiffness: 100, delay: 0.1 }}
        className="text-gray-300 mb-12 text-center max-w-2xl"
      >
        Select the platform that best suits your data needs and let's get started
      </motion.p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl w-full">
        {dataWarehouses.map((warehouse, index) => (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.2 }}
            key={warehouse.name}
          >
            <Link
              to="/connect"
              className="block"
              onMouseEnter={() => setHoveredWarehouse(warehouse.name)}
              onMouseLeave={() => setHoveredWarehouse(null)}
            >
              <motion.div 
                whileHover={{ scale: 1.05 }}
                className={`bg-gradient-to-br ${warehouse.color} rounded-xl shadow-xl p-6 h-full`}
              >
                <div className="bg-white/10 rounded-lg p-6 backdrop-blur-sm">
                  <div className="bg-white rounded-full p-4 w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                    <img 
                      src={warehouse.logo} 
                      alt={warehouse.name} 
                      className="h-16 w-auto object-contain" 
                    />
                  </div>
                  <h2 className="text-2xl font-bold text-white text-center mb-3">
                    {warehouse.name}
                  </h2>
                  <p className="text-white/80 text-center mb-4">
                    {warehouse.description}
                  </p>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: hoveredWarehouse === warehouse.name ? 1 : 0 }}
                    className="flex items-center justify-center text-white"
                  >
                    <span className="mr-2">Connect Now</span>
                    <FaArrowRight />
                  </motion.div>
                </div>
              </motion.div>
            </Link>
          </motion.div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
        className="mt-12 text-center"
      >
        <p className="text-gray-400 text-sm">
          Don't see your preferred data warehouse? 
          <a href="#" className="text-blue-400 ml-2 hover:text-blue-300">
            Contact us for custom integration
          </a>
        </p>
      </motion.div>
    </motion.div>
  )
}

export default Choose
