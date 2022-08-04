require 'digest/sha1'

def filter(event)
    hs = event.get('[result][paths]').first()
    dest = even.get('[dest]')

    c = 1
    path_complete = true
    hops = []
    ttls = []
    asns = []
    rtts = []
    hs.each do |h|
        if h.length > 0
            hops.push(h["ip"])
            rtts.push(h["rtt"][2,6].to_f * 1000)
            ttls.push(c)
            if h["as"]
                asns.push(h["as"]["number"])
            else
                asns.push(0)
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

    if hops.last() == dest
        hops.pop()

    event.set('route-sha1', Digest::SHA1.hexdigest hops.join(''))
    return [event]
end