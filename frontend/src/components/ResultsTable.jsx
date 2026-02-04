import './ResultsTable.css'

function ResultsTable({ data, columns, sql, explanation, rowCount }) {
  if (!data || data.length === 0) {
    return (
      <div className="results-container">
        {explanation && (
          <div className="query-explanation">
            <strong>Query:</strong> {explanation}
          </div>
        )}
        {sql && (
          <div className="sql-query">
            <code>{sql}</code>
          </div>
        )}
        <div className="no-results">
          No results found for this query.
        </div>
      </div>
    )
  }

  return (
    <div className="results-container">
      {explanation && (
        <div className="query-explanation">
          <strong>Query:</strong> {explanation}
        </div>
      )}
      
      {sql && (
        <div className="sql-query">
          <strong>SQL:</strong> <code>{sql}</code>
        </div>
      )}
      
      <div className="results-summary">
        Found <strong>{rowCount}</strong> result{rowCount !== 1 ? 's' : ''}
      </div>

      <div className="table-wrapper">
        <table className="results-table">
          <thead>
            <tr>
              {columns.map((col, idx) => (
                <th key={idx}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIdx) => (
              <tr key={rowIdx}>
                {columns.map((col, colIdx) => (
                  <td key={colIdx}>{row[col] ?? 'N/A'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default ResultsTable
