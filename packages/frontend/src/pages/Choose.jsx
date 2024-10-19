import React from 'react'
import { Link } from 'react-router-dom'

const Choose = () => {
  const dataWarehouses = [
    { name: 'Snowflake', logo: 'https://www.snowflake.com/wp-content/themes/snowflake/assets/img/snowflake-logo-blue.svg' },
    { name: 'Amazon Redshift', logo: 'https://d1.awsstatic.com/Products/product-name/diagrams/product-page-diagram-Amazon-Redshift_HIW.cf2d4d3494f9b1a65d4bf950496ceb37c8f7c046.png' },
    { name: 'Google BigQuery', logo: 'https://www.gstatic.com/devrel-devsite/prod/v2f6fb68338062e7c16672db62c4ab042dcb9bfbacf2fa51b6959426b203a4d8a/cloud/images/favicons/onecloud/apple-icon.png' },
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
