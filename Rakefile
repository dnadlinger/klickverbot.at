# -*- coding: utf-8 -*-

source_dir = "src"
intermediate_dir = "intermediate"
deploy_dir = "deploy"
tag_dir = "blog/tags"

task :build do
  sh "rm -rf _site"
  sh "jekyll"
end

desc "Serve on Localhost with port 4000"
task :default do
  sh "jekyll --server --auto"
end

desc "Deploy to default site"
task :deploy => :"deploy:live"

namespace :deploy do
  def rsync(host, domain)
    sh "rsync -rtvz --delete _site/ #{host}:~/#{domain}/"
  end

  desc "Deploy to live site"
  task :live => :build do
    rsync("klickverbot.at", "klickverbot.at")
  end
end

desc 'Generate tags pages'
task :tags do
  puts "Generating tags..."
  require 'rubygems'
  require 'jekyll'
  include Jekyll::Filters

  options = Jekyll.configuration({})
  site = Jekyll::Site.new(options)
  site.read_posts('')

  # Remove tags directory before regenerating
  FileUtils.rm_rf("#{source_dir}/#{tag_dir}")

  site.tags.sort.each do |tag, posts|
    FileUtils.mkdir_p("#{source_dir}/#{tag_dir}/#{tag}")
    File.open("#{source_dir}/#{tag_dir}/#{tag}/index.html", 'w+') do |file|
      file.puts <<-HTML
---
layout: default
title: "Tag archive: #{tag}"
---
<h1>Posts tagged with »#{tag}«</h1>

{% for post in site.tags["#{tag}"] %}
{% include post-excerpt.html %}
{% endfor %}
HTML
    end

    File.open("#{source_dir}/#{tag_dir}/#{tag}/atom.xml", 'w+') do |file|
      file.puts <<-ATOM
---
layout: nil
---
<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
 <title>{{ site.title }}</title>
 <link href="{{ site.url }}/#{tag_dir}/#{tag}/atom.xml" rel="self"/>
 <link href="{{ site.url }}/"/>
 <updated>{{ site.time | date_to_xmlschema }}</updated>
 <id>{{ site.url }}/#{tag_dir}/#{tag}/</id>
 <author>
   <name>David Nadlinger</name>
   <email>atom@klickverbot.at</email>
 </author>

 {% for post in site.tags["#{tag}"] %}
 <entry>
   <title>{{ post.title }}</title>
   <link href="{{ site.url }}{{ post.url }}"/>
   <updated>{{ post.date | date_to_xmlschema }}</updated>
   <id>{{ site.url }}{{ post.id }}</id>
   <content type="html">{{ post.content | xml_escape }}</content>
 </entry>
 {% endfor %}
</feed>
ATOM
    end
  end
  puts 'Done.'
end

desc 'Generate tag cloud and tag pages'
task :tagcloud do
  puts 'Generating tag cloud...'
  require 'rubygems'
  require 'jekyll'
  include Jekyll::Filters

  options = Jekyll.configuration({})
  site = Jekyll::Site.new(options)
  site.read_posts('')

  html = '<ul class="tagcloud">'
  max_count = site.tags.map{|t,p| p.count}.max
  site.tags.sort.each do |tag, posts|
    s = posts.count
    font_size = ((20 - 10.0*(max_count-s)/max_count)*2).to_i/2.0
    url = "/#{tag_dir}/#{tag}/"
    html << "<li><a href=\"#{URI.escape url}\" title=\"View posts tagged #{tag}\" style=\"font-size: #{font_size}px; line-height:#{font_size}px\">#{tag}</a></li>"
  end
  html << '</ul>'
  File.open('_includes/tagcloud.html', 'w+') do |file|
    file.puts html
  end
  puts 'Done.'
end

desc 'Optimize style PNGs'
task :optimize_pngs do
  sh "open -a ImageOptim.app style/*.png"
end

desc 'Rename photo gallery files to their public names'
task :rename_photos do
  MAPPING = {
    "DSC_0082.jpg" => "two-at-the-beach.jpg",
    "DSC_0692.jpg" => "back-to-the-drawing-board.jpg",
    "DSC_0903.jpg" => "clash-of-generations.jpg",
    "IMG_0264.jpg" => "rocky-2010-janet.jpg",
    "IMG_0281.jpg" => "rocky-2010-rocky-janet.jpg",
    "IMG_2634.jpg" => "blooming-like-the-sun.jpg",
    "IMG_3041.jpg" => "talking-big.jpg",
    "IMG_3372.jpg" => "of-public-interest.jpg",
    "IMG_3694.jpg" => "alice.jpg",
    "IMG_6185.jpg" => "eau-non-potable.jpg",
    "IMG_6536.jpg" => "louvre.jpg",
    "IMG_6970.jpg" => "gaze.jpg",
    "IMG_8272.jpg" => "veins.jpg",
    "IMG_8281.jpg" => "icicles.jpg",
    "IMG_8340-Edit.jpg" => "koma.jpg",
    "Portrait Ina.jpg" => "smiling.jpg",
  }

  MAPPING.keys.each do |source|
    File.rename( "visual/small/#{source}", "visual/small/#{MAPPING[ source ]}" )
    File.rename( "visual/large/#{source}", "visual/large/#{MAPPING[ source ]}" )
  end
end
