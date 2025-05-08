#!/usr/bin/env ruby

# =====================================================================
# Direct Homebrew Command Helper for py-winmail-opener
# =====================================================================
# This script directly executes problematic brew operations without
# going through the Homebrew CLI layer that's causing the errors
# =====================================================================

require 'pathname'
require 'fileutils'

class HomebrewDirectCommands
  FORMULA_NAME = "py-winmail-opener"
  HOMEBREW_PREFIX = Pathname.new("/usr/local")
  HOMEBREW_CELLAR = HOMEBREW_PREFIX/"Cellar"
  
  def initialize
    @formula_version = find_installed_version || "unknown"
    @formula_path = HOMEBREW_CELLAR/FORMULA_NAME/@formula_version
    
    puts "Working with formula: #{FORMULA_NAME}"
    puts "Installed version: #{@formula_version}"
    puts "Formula path: #{@formula_path}"
    puts ""
  end
  
  def find_installed_version
    if HOMEBREW_CELLAR.directory?
      formula_dir = HOMEBREW_CELLAR/FORMULA_NAME
      return nil unless formula_dir.directory?
      
      versions = Dir.entries(formula_dir).reject { |entry| entry.start_with?('.') }
      return versions.first if versions.any?
    end
    nil
  end
  
  def find_venv_path
    if @formula_path.directory?
      venv_path = @formula_path/"libexec"/"venv"
      return venv_path if venv_path.directory?
    end
    nil
  end
  
  def find_installed_files
    files = []
    
    # Check binary symlinks
    bin_dir = HOMEBREW_PREFIX/"bin"
    if bin_dir.directory?
      Dir.glob("#{bin_dir}/*").each do |file|
        if File.symlink?(file) && File.readlink(file).include?(FORMULA_NAME)
          files << file
        end
      end
    end
    
    # Check formula directory
    if @formula_path.directory?
      files << @formula_path.to_s
    end
    
    files
  end
  
  def uninstall
    puts "=== Uninstalling #{FORMULA_NAME} ==="
    
    venv_path = find_venv_path
    if venv_path
      # Run the custom uninstaller if available
      uninstall_script = @formula_path/"uninstall.py"
      if uninstall_script.file?
        puts "Running custom uninstaller script..."
        system "#{venv_path}/bin/python", uninstall_script.to_s, "--homebrew-mode", "--force"
      end
    end
    
    # Remove installed files
    installed_files = find_installed_files
    if installed_files.any?
      puts "Removing installed files..."
      installed_files.each do |file|
        if File.directory?(file)
          puts "  Removing directory: #{file}"
          FileUtils.rm_rf(file)
        else
          puts "  Removing file: #{file}"
          FileUtils.rm_f(file)
        end
      end
      puts "Done removing files."
    else
      puts "No installed files found."
    end
    
    puts "=== Uninstallation complete ==="
  end
  
  def reinstall
    puts "=== Reinstalling #{FORMULA_NAME} ==="
    puts "To reinstall, first uninstall then install fresh"
    uninstall
    
    puts "\nTo install a fresh copy, run:"
    puts "  brew install jsbattig/winmail/py-winmail-opener"
    puts "=== Reinstall operation complete ==="
  end
end

# Main
if ARGV.length != 1
  puts "Usage: #{$0} [uninstall|reinstall]"
  exit 1
end

command = ARGV[0]
helper = HomebrewDirectCommands.new

case command
when "uninstall"
  helper.uninstall
when "reinstall"
  helper.reinstall
else
  puts "Unknown command: #{command}"
  puts "Usage: #{$0} [uninstall|reinstall]"
  exit 1
end
