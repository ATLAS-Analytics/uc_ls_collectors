def filter(event)
    hs = event.get('[result][paths]').first
    c = 1
    hops = []
    ttls = []
    asns = []
    rtts = []
    hs.each do |h|
        puts "#{person[:name]}: #{person[:occupation]}"
        hops.push(h[:ip])
        ttls.push(c)
        asns.push(h[:as][:number])
        rtts.push(h[:rtt])
        c = c + 1
    end
    event.set('hops', hops)
    event.set('ttls', ttls)
    event.set('asns', asns)
    event.set('rtts', rtts)
    return [event]
end