import { apiClient } from './client';

export interface AttendanceRow {
  fecha_hora: string;
  usuario_id: number;
  usuario_nombre: string | null;
  resultado: string;
  tipo_membresia: string | null;
  titular_nombre: string | null;
}

export interface AttendanceFilters {
  fecha_inicio: string;
  fecha_fin: string;
}

export type ExportFormat = 'xlsx' | 'csv';

export async function getAttendanceReport(filters: AttendanceFilters): Promise<AttendanceRow[]> {
  const { data } = await apiClient.get<AttendanceRow[]>('/reportes/attendance', { params: filters });
  return data;
}

export async function exportAttendanceReport(
  filters: AttendanceFilters,
  format: ExportFormat,
): Promise<void> {
  const { data } = await apiClient.get<Blob>('/reportes/attendance/export', {
    params: { ...filters, format },
    responseType: 'blob',
  });
  const url = URL.createObjectURL(data);
  const link = document.createElement('a');
  link.href = url;
  link.download = `asistencias_${filters.fecha_inicio}_${filters.fecha_fin}.${format}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
