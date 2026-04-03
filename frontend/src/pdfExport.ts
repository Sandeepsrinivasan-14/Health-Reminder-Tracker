import jsPDF from 'jspdf'

export class PDFExportService {
  static exportHealthReport(healthData: any[], userName: string) {
    const doc = new jsPDF()
    
    doc.setFontSize(20)
    doc.text('Health Report', 105, 20, { align: 'center' })
    
    doc.setFontSize(12)
    doc.text('Patient: ' + userName, 20, 40)
    doc.text('Date: ' + new Date().toLocaleDateString(), 20, 50)
    
    let yPos = 70
    doc.text('Date | BP | Heart Rate | Sugar | Weight', 20, yPos)
    
    healthData.slice(-10).forEach(data => {
      yPos += 10
      doc.text(data.date + ' | ' + data.bp_systolic + '/' + data.bp_diastolic + ' | ' + data.heart_rate + ' | ' + data.blood_sugar + ' | ' + data.weight + 'kg', 20, yPos)
    })
    
    doc.save('health_report_' + userName + '.pdf')
    alert('PDF Report Downloaded!')
  }
}
