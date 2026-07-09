import { isAxiosError } from 'axios';
import { useMutation } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';

import { DispositivoBloqueadoError, postCheckin, type CheckinResponse } from '../api/checkin';
import NumericKeypad from './NumericKeypad';

const REINICIO_MS = 4000;

type Resultado = CheckinResponse | { resultado: 'denegado'; mensaje: string; razon: null };

function CheckinKiosk() {
  const [cedula, setCedula] = useState('');
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [bloqueadoHasta, setBloqueadoHasta] = useState<Date | null>(null);
  const reinicioRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const mutation = useMutation({
    mutationFn: postCheckin,
    onSuccess: (data) => mostrarResultado(data),
    onError: (error) => {
      if (error instanceof DispositivoBloqueadoError) {
        setBloqueadoHasta(error.bloqueadoHasta);
        setCedula('');
        return;
      }
      const noEncontrado = isAxiosError(error) && error.response?.status === 404;
      mostrarResultado({
        resultado: 'denegado',
        mensaje: noEncontrado
          ? 'Cédula no registrada. Dirígete a recepción.'
          : 'No se pudo validar el ingreso. Intenta de nuevo.',
        razon: null,
      });
    },
  });

  function mostrarResultado(data: Resultado) {
    setResultado(data);
    setCedula('');
    reinicioRef.current = setTimeout(() => setResultado(null), REINICIO_MS);
  }

  function handleSubmit() {
    if (cedula.length === 0 || mutation.isPending) return;
    mutation.mutate(cedula);
  }

  if (bloqueadoHasta) {
    return <PantallaBloqueo hasta={bloqueadoHasta} onExpira={() => setBloqueadoHasta(null)} />;
  }

  if (resultado) {
    const exitoso = resultado.resultado === 'exitoso';
    return (
      <div
        className={`min-h-screen flex items-center justify-center p-8 ${
          exitoso ? 'bg-green-600' : 'bg-red-600'
        }`}
      >
        <p className="text-white text-4xl font-bold text-center leading-snug">
          {resultado.mensaje}
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-member-bg flex items-center justify-center p-8">
      <div className="bg-white rounded-card shadow-md p-10 w-full max-w-md text-center">
        <h1 className="text-member-navy-text text-2xl font-bold">GymFlow</h1>
        <p className="text-member-muted mt-1 mb-6">Ingresa tu número de cédula</p>

        <div className="h-16 rounded-card bg-member-bg text-member-navy-text text-3xl font-mono flex items-center justify-center tracking-widest mb-6">
          {cedula || '—'}
        </div>

        <NumericKeypad
          disabled={mutation.isPending}
          onDigit={(d) => setCedula((prev) => (prev.length < 20 ? prev + d : prev))}
          onBackspace={() => setCedula((prev) => prev.slice(0, -1))}
          onSubmit={handleSubmit}
        />
      </div>
    </div>
  );
}

function PantallaBloqueo({ hasta, onExpira }: { hasta: Date; onExpira: () => void }) {
  const [restanteMs, setRestanteMs] = useState(() => hasta.getTime() - Date.now());

  useEffect(() => {
    const id = setInterval(() => {
      const restante = hasta.getTime() - Date.now();
      setRestanteMs(restante);
      if (restante <= 0) onExpira();
    }, 1000);
    return () => clearInterval(id);
  }, [hasta, onExpira]);

  const totalSeg = Math.max(0, Math.ceil(restanteMs / 1000));
  const minutos = String(Math.floor(totalSeg / 60)).padStart(2, '0');
  const segundos = String(totalSeg % 60).padStart(2, '0');

  return (
    <div className="min-h-screen bg-red-700 flex flex-col items-center justify-center p-8 gap-6">
      <p className="text-white text-3xl font-bold text-center">
        Dispositivo bloqueado temporalmente.
      </p>
      <p className="text-white/90 text-xl text-center">
        Demasiados intentos fallidos. Intenta de nuevo en:
      </p>
      <p className="text-white text-6xl font-mono font-bold tabular-nums">
        {minutos}:{segundos}
      </p>
    </div>
  );
}

export default CheckinKiosk;
