interface NumericKeypadProps {
  onDigit: (digit: string) => void;
  onBackspace: () => void;
  onSubmit: () => void;
  disabled?: boolean;
}

const DIGITS = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'borrar', '0', 'enviar'];

// Botones táctiles grandes (≥48x48px, RNF usabilidad de tech-stack.md) para
// que el kiosko no dependa de un teclado físico.
function NumericKeypad({ onDigit, onBackspace, onSubmit, disabled }: NumericKeypadProps) {
  return (
    <div className="grid grid-cols-3 gap-4">
      {DIGITS.map((key) => {
        if (key === 'borrar') {
          return (
            <button
              key={key}
              type="button"
              disabled={disabled}
              onClick={onBackspace}
              className="h-20 rounded-card bg-member-bg text-member-navy-text text-xl font-semibold active:scale-95 transition disabled:opacity-50"
            >
              Borrar
            </button>
          );
        }
        if (key === 'enviar') {
          return (
            <button
              key={key}
              type="button"
              disabled={disabled}
              onClick={onSubmit}
              className="h-20 rounded-card bg-member-navy text-white text-xl font-semibold active:scale-95 transition disabled:opacity-50"
            >
              Ingresar
            </button>
          );
        }
        return (
          <button
            key={key}
            type="button"
            disabled={disabled}
            onClick={() => onDigit(key)}
            className="h-20 rounded-card bg-white text-member-navy-text text-3xl font-bold shadow active:scale-95 transition disabled:opacity-50"
          >
            {key}
          </button>
        );
      })}
    </div>
  );
}

export default NumericKeypad;
