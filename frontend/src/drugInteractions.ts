export const drugInteractions: {[key: string]: string[]} = {
  'warfarin': ['aspirin', 'ibuprofen', 'paracetamol'],
  'aspirin': ['warfarin', 'ibuprofen'],
  'ibuprofen': ['warfarin', 'aspirin'],
  'metformin': ['insulin'],
  'insulin': ['metformin']
}

export function checkInteraction(drugs: string[]): string[] {
  const warnings: string[] = []
  
  for (let i = 0; i < drugs.length; i++) {
    for (let j = i + 1; j < drugs.length; j++) {
      const drug1 = drugs[i].toLowerCase()
      const drug2 = drugs[j].toLowerCase()
      
      if (drugInteractions[drug1] && drugInteractions[drug1].includes(drug2)) {
        warnings.push('?? Potential interaction: ' + drugs[i] + ' + ' + drugs[j])
      }
      if (drugInteractions[drug2] && drugInteractions[drug2].includes(drug1)) {
        warnings.push('?? Potential interaction: ' + drugs[j] + ' + ' + drugs[i])
      }
    }
  }
  
  return warnings
}
