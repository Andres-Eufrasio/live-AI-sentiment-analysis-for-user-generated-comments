import { useState, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [test, setTest] = useState([])
  const [connection, setConnection] = useState("No connection found")




  // function single
  useEffect(() =>{
    fetch("http://host.docker.internal:8000")
    .then((data) => data.json())
    .then((data) => {setConnection(data.Connection);

    });

  }
  );


  
  return (
    <>
      <section id="test_section">

        <div>
          <h1>This is a basic test of my system</h1>
          
          <p>
            {connection}
          </p>
        </div>

      </section>


    </>
  )
}

export default App
