require 'digest/sha1'
require 'ipaddr'

def normalize_ip(ip)
  ip = ip.split.join("") # we have cases like this: "2001:b30: 4202: 100: : 3", that this library can not handle and identify like this "2001:b30:4202:100::3"
  IPAddr.new(ip).to_s.downcase
rescue
  ip.downcase
end

def same_ip?(a, b)
  normalized_a = normalize_ip(a)
  normalized_b = normalize_ip(b)
  normalized_a == normalized_b
rescue
  false
end

def filter(event)
    hs = event.get('[result][paths]').first()
    dest = event.get('[dest]')

# TODO add lookups for dns names from memcached.
    c = 1
    path_complete = true
    destination_reached = false
    hops = []
    ttls = []
    asns = []
    rtts = []
    hs.each do |h|
        if h.length > 0
            hops.push(h["ip"].strip)
            rtts.push(h["rtt"][2,6].to_f * 1000)
            ttls.push(c)
            if h["as"]
                asns.push(h["as"]["number"])
            else
                asns.push(0)
                # TODO here do an asns lookup 
            end
        else
            path_complete = false
        end
        c += 1
    end

    event.set('path_complete', path_complete)
    event.set('hops', hops)
    event.set('ttls', ttls)
    event.set('asns', asns)
    event.set('rtts', rtts)
    event.set('max_rtt', rtts.max)
    event.set('looping',hops.uniq.length!=hops.length)
  
    if !hops.empty? && dest
        if same_ip?(hops.last, dest)
            destination_reached = true
        end
    end

    event.set('destination_reached', destination_reached)
    event.set('route-sha1', Digest::SHA1.hexdigest(hops.join('')))
    return [event]
end
