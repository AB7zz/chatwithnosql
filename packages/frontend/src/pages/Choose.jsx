import React from 'react'
import { Link } from 'react-router-dom'

const Choose = () => {
  const dataWarehouses = [
    { name: 'Snowflake', logo: 'https://companieslogo.com/img/orig/SNOW-35164165.png?t=1720244494' },
    { name: 'Amazon Redshift', logo: 'https://cdn.prod.website-files.com/625447c67b621ab49bb7e3e5/6511e6855e26e61247127ecb_63bdba82fbba1214de98c30d_1862px-Amazon-Redshift-Logo.svg%255B1%255D.png' },
    { name: 'Google BigQuery', logo: 'https://cdn.worldvectorlogo.com/logos/google-bigquery-logo-1.svg' },
  ]

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Choose a Data Warehouse</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {dataWarehouses.map((warehouse) => (
          <Link
            key={warehouse.name}
            to="/connect"
            className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-300 overflow-hidden"
          >
            <div className="p-6 flex flex-col items-center">
              <img src={warehouse.logo} alt={warehouse.name} className="h-24 w-auto mb-4" />
              <h2 className="text-xl font-semibold text-gray-700">{warehouse.name}</h2>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Choose
