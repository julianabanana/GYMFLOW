import { useMutation, useQuery } from '@tanstack/react-query';
import { useState, type FormEvent } from 'react';

import {
  exportAttendanceReport,
  getAttendanceReport,
  type AttendanceFilters,
  type ExportFormat,
} from '../../api/reports';
import { useAuth } from '../../context/useAuth';

function hoyISO(): string {
  return new Date().toISOString().slice(0, 10);
}

function primerDiaDelMesISO(): string {
  const ahora = new Date();
  return new Date(ahora.getFullYear(), ahora.getMonth(), 1).toISOString().slice(0, 10);
}

function AttendanceReportPage() {
  const auth = useAuth();
  const esAdmin = auth.rol === 'administrador';

  const [form, setForm] = useState<AttendanceFilters>({
    fecha_inicio: primerDiaDelMesISO(),
    fecha_fin: hoyISO(),
  });
  const [filtros, setFiltros] = useState<AttendanceFilters | null>(null);

  const reporte = useQuery({
    queryKey: ['reporte-asistencias', filtros],
    queryFn: () => getAttendanceReport(filtros as AttendanceFilters),
    enabled: esAdmin && filtros !== null,
  });

  const exportar = useMutation({
    mutationFn: (formato: ExportFormat) => exportAttendanceReport(form, formato),
  });

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFiltros({ ...form });
  }

  if (!esAdmin) {
    return (
      <div>
        <h1 className="text-member-navy-text text-2xl font-semibold mb-4">Reportes de asistencia</h1>
        <p className="text-red-600 bg-red-50 border border-red-200 rounded p-3">
          Solo un Administrador puede consultar los reportes de asistencia.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-member-navy-text text-2xl font-semibold mb-4">Reportes de asistencia</h1>

      <form
        onSubmit={handleSubmit}
        className="bg-white rounded-card shadow border border-gray-200 p-4 mb-6 flex flex-wrap items-end gap-3"
      >
        <div>
          <label className="block text-xs text-gray-600 mb-1" htmlFor="inicio">Fecha inicio</label>
          <input
            id="inicio" type="date" required value={form.fecha_inicio}
            onChange={(e) => setForm({ ...form, fecha_inicio: e.target.value })}
            className="border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <div>
          <label className="block text-xs text-gray-600 mb-1" htmlFor="fin">Fecha fin</label>
          <input
            id="fin" type="date" required value={form.fecha_fin}
            onChange={(e) => setForm({ ...form, fecha_fin: e.target.value })}
            className="border border-gray-300 rounded px-2 py-1 text-sm"
          />
        </div>
        <button
          type="submit"
          className="bg-member-navy text-white rounded px-3 py-1.5 text-sm"
        >
          Consultar
        </button>
        <button
          type="button" disabled={exportar.isPending}
          onClick={() => exportar.mutate('xlsx')}
          className="text-sm text-member-navy border border-gray-300 rounded px-3 py-1.5 hover:bg-gray-50 disabled:opacity-50"
        >
          Exportar XLSX
        </button>
        <button
          type="button" disabled={exportar.isPending}
          onClick={() => exportar.mutate('csv')}
          className="text-sm text-member-navy border border-gray-300 rounded px-3 py-1.5 hover:bg-gray-50 disabled:opacity-50"
        >
          Exportar CSV
        </button>
      </form>

      {exportar.isError && (
        <p className="text-red-600 text-sm mb-4">No se pudo exportar el reporte.</p>
      )}
      {reporte.isError && (
        <p className="text-red-600 text-sm mb-4">No se pudo cargar el reporte.</p>
      )}
      {reporte.isLoading && <p className="text-gray-500">Cargando…</p>}

      {reporte.data && reporte.data.length === 0 && (
        <p className="text-gray-500">No hay asistencias en el rango seleccionado.</p>
      )}

      {reporte.data && reporte.data.length > 0 && (
        <>
          <p className="text-sm text-gray-500 mb-2">
            {reporte.data.length} asistencia(s) en el rango.
          </p>
          <table className="w-full bg-white rounded-card shadow border border-gray-200 text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b border-gray-200">
                <th className="p-3">Fecha y hora</th>
                <th className="p-3">Usuario</th>
                <th className="p-3">Resultado</th>
                <th className="p-3">Tipo de membresía</th>
                <th className="p-3">Titular</th>
              </tr>
            </thead>
            <tbody>
              {reporte.data.map((row, i) => (
                <tr key={`${row.usuario_id}-${row.fecha_hora}-${i}`} className="border-b border-gray-100 last:border-0">
                  <td className="p-3 text-gray-900">{new Date(row.fecha_hora).toLocaleString()}</td>
                  <td className="p-3 text-gray-900">{row.usuario_nombre ?? `#${row.usuario_id}`}</td>
                  <td className="p-3 text-gray-900">{row.resultado}</td>
                  <td className="p-3 text-gray-900">{row.tipo_membresia ?? '—'}</td>
                  <td className="p-3 text-gray-900">{row.titular_nombre ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </div>
  );
}

export default AttendanceReportPage;
