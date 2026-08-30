function Stat({ title, value }) {
  return (
    <div className="stat">
      <span>{title} </span>
      <strong>{value}</strong>
    </div>
  );
}

export default Stat;