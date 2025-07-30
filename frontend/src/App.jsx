import { useState } from 'react';

function App() {
  const [email, setEmail] = useState('');
  const [city, setCity] = useState('New York City');
  const [zip, setZip] = useState('');
  const [permitType, setPermitType] = useState('General Construction');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2025-07-29');
  const [status, setStatus] = useState('');

  const handleSubmit = async () => {
    setStatus('Running ETL, please wait...');

    try {
      const response = await fetch('http://localhost:8000/run-etl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, city, zip_code: zip, permit_type: permitType, start_date: startDate, end_date: endDate })
      });

      const data = await response.json();
      setStatus(data.message || 'Done');
    } catch (error) {
      console.error(error);
      setStatus('Error running ETL.');
    }
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto', padding: '2rem' }}>
      <h1>🏙️ NYC Permit ETL Dashboard</h1>
      <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} /><br /><br />
      <select value={city} onChange={e => setCity(e.target.value)}>
        <option>New York City</option>
        <option>San Francisco</option>
        <option>Chicago</option>
      </select><br /><br />
      <input type="text" placeholder="ZIP Code (optional)" value={zip} onChange={e => setZip(e.target.value)} /><br /><br />
      <select value={permitType} onChange={e => setPermitType(e.target.value)}>
        <option>General Construction</option>
        <option>Sidewalk Shed</option>
      </select><br /><br />
      <label>Start Date: <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} /></label><br /><br />
      <label>End Date: <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} /></label><br /><br />
      <button onClick={handleSubmit}>Run ETL</button>
      <p>{status}</p>
    </div>
  );
}

export default App;

