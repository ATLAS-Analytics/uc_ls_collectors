def filter(event)
    # hs = event.get('[result][paths]').first
    c = 1
    # hops = []
    # ttls = []
    # asns = []
    # rtts = []
    # hops.push(1)
    # hops.push(2)
    # hops.push(3)
    # hs.each do |h|
    #     hops.push(h[:ip])
    #     ttls.push(c)
    #     asns.push(h[:as][:number])
    #     rtts.push(h[:rtt])
    #     c = c + 1
    # end
    event.set('hops', c)
    # event.set('ttls', ttls)
    # event.set('asns', asns)
    # event.set('rtts', rtts)
    return [event]
end