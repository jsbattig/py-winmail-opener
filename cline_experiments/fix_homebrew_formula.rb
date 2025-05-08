#!/usr/bin/env ruby

# =====================================================================
# Direct Formula Fix for py-winmail-opener Homebrew Formula
# =====================================================================
# This script directly modifies the formula file to fix the uninstall method
# signature issue causing the "wrong number of arguments" error
# =====================================================================

require 'fileutils'

class FormulaFixer
  HOMEBREW_PREFIX = "/usr/local"
  TAP_PATH = "#{HOMEBREW_PREFIX}/Homebrew/Library/Taps/jsbattig/homebrew-winmail"
  FORMULA_PATH = "#{TAP_PATH}/py-winmail-opener.rb"
  BACKUP_PATH = "#{FORMULA_PATH}.original"
  
  def initialize
    check_formula_exists
    create_backup
  end
  
  def check_formula_exists
    unless File.exist?(FORMULA_PATH)
      puts "Error: Formula not found at #{FORMULA_PATH}"
      puts "Make sure the tap is installed with: brew tap jsbattig/winmail"
      exit 1
    end
  end
  
  def create_backup
    unless File.exist?(BACKUP_PATH)
      puts "Creating backup of original formula..."
      FileUtils.cp(FORMULA_PATH, BACKUP_PATH)
      puts "Backup created at #{BACKUP_PATH}"
    else
      puts "Using existing backup at #{BACKUP_PATH}"
    end
  end
  
  def read_formula
    File.read(FORMULA_PATH)
  end
  
  def write_formula(content)
    File.write(FORMULA_PATH, content)
  end
  
  def fix_uninstall_method
    puts "Fixing uninstall method signature..."
    
    content = read_formula
    
    # Check if it already has the fix
    if content.match?(/def\s+uninstall\s*\(.*\)/)
      puts "Formula already has the correct uninstall method signature"
      return false
    end
    
    # Apply the fix - replace 'def uninstall' with 'def uninstall(args=nil)'
    fixed_content = content.gsub(/def\s+uninstall\s*$/, 'def uninstall(args=nil)')
    
    if fixed_content == content
      puts "No changes needed or pattern not found"
      return false
    else
      write_formula(fixed_content)
      puts "Formula updated successfully"
      return true
    end
  end
  
  def verify_fix
    puts "Verifying fix..."
    content = read_formula
    if content.match?(/def\s+uninstall\s*\(.*\)/)
      puts "✅ Verification successful: Formula now has the correct uninstall method signature"
      true
    else
      puts "❌ Verification failed: Formula still has the incorrect uninstall method signature"
      false
    end
  end
  
  def restore_backup
    if File.exist?(BACKUP_PATH)
      puts "Restoring from backup..."
      FileUtils.cp(BACKUP_PATH, FORMULA_PATH)
      puts "Original formula restored"
    else
      puts "No backup found, cannot restore"
    end
  end
end

# Run the fixer
puts "==============================================="
puts "Py-Winmail-Opener Formula Fixer"
puts "==============================================="

fixer = FormulaFixer.new

if ARGV.include?("--restore")
  fixer.restore_backup
  exit 0
end

puts "Fixing formula..."
fixed = fixer.fix_uninstall_method
verified = fixer.verify_fix

if fixed && verified
  puts "==============================================="
  puts "Formula successfully fixed!"
  puts "Try running:"
  puts "  brew reinstall py-winmail-opener"
  puts ""
  puts "If you want to restore the original formula, run:"
  puts "  #{__FILE__} --restore"
  puts "==============================================="
else
  puts "==============================================="
  puts "Formula fix didn't succeed or wasn't needed"
  puts "You may need to try an alternative approach"
  puts "==============================================="
end
