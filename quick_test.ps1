Write-Host "`n🔔 QUICK NOTIFICATION SYSTEM TEST" -ForegroundColor Cyan
Write-Host "=" * 60

# 1. Check backend health
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -ErrorAction Stop
    Write-Host "✅ Backend Health: $($response.status)" -ForegroundColor Green
    $backendRunning = $true
} catch {
    Write-Host "❌ Backend not responding! Make sure it's running." -ForegroundColor Red
    $backendRunning = $false
}

if ($backendRunning) {
    # 2. Check medication reminders
    Write-Host "`n💊 Checking Medication Reminders:" -ForegroundColor Yellow
    try {
        $meds = Invoke-RestMethod -Uri "http://localhost:8000/api/notifications/medication-reminders/1" -ErrorAction Stop
        Write-Host "   Time of day: $($meds.time_of_day)" -ForegroundColor White
        Write-Host "   Medications due: $($meds.medications.Count)" -ForegroundColor White
        if ($meds.medications.Count -gt 0) {
            foreach ($med in $meds.medications) {
                Write-Host "   → $($med.name) - $($med.dosage)" -ForegroundColor Green
            }
        } else {
            Write-Host "   → No medications due at this time" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ⚠️ Could not check medications: $_" -ForegroundColor Yellow
    }

    # 3. Check vaccination reminders
    Write-Host "`n💉 Checking Vaccination Reminders:" -ForegroundColor Yellow
    try {
        $vax = Invoke-RestMethod -Uri "http://localhost:8000/api/notifications/vaccination-due/1" -ErrorAction Stop
        Write-Host "   Vaccinations due: $($vax.vaccinations.Count)" -ForegroundColor White
        if ($vax.vaccinations.Count -gt 0) {
            foreach ($v in $vax.vaccinations) {
                Write-Host "   → $($v.name) - Due: $($v.due_date)" -ForegroundColor Green
            }
        } else {
            Write-Host "   → No vaccinations due in next 7 days" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ⚠️ Could not check vaccinations: $_" -ForegroundColor Yellow
    }

    # 4. Check existing alerts
    Write-Host "`n⚠️ Current Health Alerts:" -ForegroundColor Yellow
    try {
        $alerts = Invoke-RestMethod -Uri "http://localhost:8000/api/notifications/alerts/1" -ErrorAction Stop
        Write-Host "   Total alerts: $($alerts.Count)" -ForegroundColor White
        if ($alerts.Count -gt 0) {
            foreach ($alert in $alerts) {
                $icon = if ($alert.level -eq 'danger') { '🔴' } elseif ($alert.level -eq 'warning') { '🟡' } else { '🔵' }
                $msg = if ($alert.message.Length -gt 50) { $alert.message.Substring(0, 50) + "..." } else { $alert.message }
                Write-Host "   $icon $($alert.type): $msg" -ForegroundColor White
                Write-Host "      Created: $($alert.created_at)" -ForegroundColor Gray
                Write-Host "      Acknowledged: $(if($alert.acknowledged){'Yes'}else{'No'})" -ForegroundColor Gray
            }
        } else {
            Write-Host "   → No active alerts" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ⚠️ Could not check alerts: $_" -ForegroundColor Yellow
    }

    # 5. Check notification settings
    Write-Host "`n⚙️ Notification Settings:" -ForegroundColor Yellow
    try {
        $settings = Invoke-RestMethod -Uri "http://localhost:8000/api/notifications/settings/1" -ErrorAction Stop
        Write-Host "   Browser Notifications: $(if($settings.browser_notifications){'✅ ON'}else{'❌ OFF'})" -ForegroundColor White
        Write-Host "   Email Notifications: $(if($settings.email_notifications){'✅ ON'}else{'❌ OFF'})" -ForegroundColor White
        Write-Host "   SMS Notifications: $(if($settings.sms_notifications){'✅ ON'}else{'❌ OFF'})" -ForegroundColor White
        Write-Host "   Reminder Frequency: $($settings.reminder_frequency)" -ForegroundColor White
    } catch {
        Write-Host "   ⚠️ Could not check settings: $_" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n" + "=" * 60
Write-Host "📊 TEST SUMMARY:" -ForegroundColor Cyan
Write-Host "✅ Backend: $(if($backendRunning){'Running'}else{'Not Running'})" -ForegroundColor $(if($backendRunning){'Green'}else{'Red'})

if ($backendRunning) {
    Write-Host "✅ Database: $(if(Test-Path 'health_tracker.db'){'OK'}else{'Missing'})" -ForegroundColor Green
    Write-Host "✅ Medication Reminders: $(if($meds.medications.Count -gt 0){'Active'}else{'No due medications'})" -ForegroundColor Yellow
    Write-Host "✅ Vaccination Reminders: $(if($vax.vaccinations.Count -gt 0){'Active'}else{'No due vaccinations'})" -ForegroundColor Yellow
    Write-Host "✅ Health Alerts: $($alerts.Count) active" -ForegroundColor Yellow
}
Write-Host "=" * 60

# Recommendations
Write-Host "`n🎯 RECOMMENDED ACTIONS:" -ForegroundColor Magenta
if ($backendRunning) {
    if ($alerts.Count -eq 0) {
        Write-Host "1. Create a test health alert:" -ForegroundColor White
        Write-Host "   Run: python -c \"import requests; requests.post('http://localhost:8000/api/notifications/health-alert', json={'user_id':1,'alert_type':'Test','alert_level':'warning','message':'Test alert'})\"" -ForegroundColor Gray
    }
    if ($meds.medications.Count -eq 0) {
        Write-Host "2. Add a medication with time_of_day matching current time" -ForegroundColor White
        Write-Host "   Current time of day: $($meds.time_of_day)" -ForegroundColor Gray
    }
    if ($vax.vaccinations.Count -eq 0) {
        Write-Host "3. Add a vaccination with due date within next 7 days" -ForegroundColor White
    }
} else {
    Write-Host "1. Start the backend server:" -ForegroundColor White
    Write-Host "   uvicorn backend:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Gray
}

Write-Host "`n📚 Useful Commands:" -ForegroundColor Cyan
Write-Host "   View API docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Check database: python check_database.py" -ForegroundColor White
Write-Host "   Run full test: python test_notifications.py" -ForegroundColor White
Write-Host "   View notification guide: Get-Content NOTIFICATION_REFERENCE_GUIDE.txt" -ForegroundColor White
