#!/usr/bin/env ruby

# This script inspects the Homebrew formula metadata to understand why
# we're getting the error: "wrong number of arguments (given 1, expected 0)"

require 'pathname'
homebrew_repo = `brew --repository`.chomp
tap_path = File.join(homebrew_repo, "Library", "Taps", "jsbattig", "homebrew-winmail")
formula_path = File.join(tap_path, "py-winmail-opener.rb")

puts "--- Formula file content ---"
puts File.read(formula_path)

puts "\n--- Loaded formulas in system ---"
puts `brew list --full-name`

puts "\n--- Path to installed formula ---"
puts `brew --cellar py-winmail-opener`.chomp

puts "\n--- Checking formula metadata ---"
puts `brew cat jsbattig/winmail/py-winmail-opener`

puts "\n--- Methods in formula ---"
cmd = <<-RUBY
require 'pathname'
require '#{homebrew_repo}/Library/Homebrew/global'
require '#{homebrew_repo}/Library/Homebrew/formula'
formula = Formulary.factory('jsbattig/winmail/py-winmail-opener')
puts "Formula defines methods: #{formula.class.instance_methods(false).sort.join(', ')}"
puts "Formula has uninstall? #{formula.class.method_defined?(:uninstall)}"
if formula.class.method_defined?(:uninstall)
  method = formula.class.instance_method(:uninstall)
  puts "Uninstall method parameters: #{method.parameters.inspect}"
end
RUBY

puts `ruby -e "#{cmd}" 2>&1`
